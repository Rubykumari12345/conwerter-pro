from flask import Flask, request, send_file, send_from_directory, jsonify
from flask_cors import CORS
import os
import zipfile
import uuid
from converter import convert_image
from pdf_converter import pdf_to_images, images_to_pdf, pdf_to_docx_convert, merge_pdfs, split_pdf, compress_pdf, docx_to_pdf_convert

app = Flask(__name__)
CORS(app, expose_headers=["Content-Disposition"])

# Folder Configuration
UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'outputs'
FRONTEND_FOLDER = '../frontend'

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# 1. Serve Frontend Pages
@app.route('/')
def serve_index():
    return send_from_directory(FRONTEND_FOLDER, 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory(FRONTEND_FOLDER, path)

@app.route('/api/health')
def health_check():
    return jsonify({"status": "ok"})

# 2. API Endpoint for Conversion
@app.route('/api/convert', methods=['POST'])
def convert_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
        
    files = request.files.getlist('file')
    conversion_type = request.form.get('conversion_type')
    
    # Advanced Options
    options = {
        'target_size': request.form.get('target_size'),
        'quality': request.form.get('quality'),
        'width': request.form.get('width'),
        'height': request.form.get('height'),
        'rotate': request.form.get('rotate'),
        'flip_h': request.form.get('flip_h'),
        'flip_v': request.form.get('flip_v')
    }
    
    if len(files) == 0 or files[0].filename == '':
        return jsonify({'error': 'No file selected'}), 400
        
    try:
        # Create a batch ID
        batch_id = str(uuid.uuid4())[:8]
        batch_output_dir = os.path.join(OUTPUT_FOLDER, batch_id)
        os.makedirs(batch_output_dir, exist_ok=True)
        
        output_paths = []
        
        # Handle Image to PDF specifically (combines all images into one PDF)
        if conversion_type == 'image_to_pdf':
            input_paths = []
            for file in files:
                input_path = os.path.join(UPLOAD_FOLDER, f"{batch_id}_{file.filename}")
                file.save(input_path)
                input_paths.append(input_path)
            
            output_filename = f"{batch_id}_converted.pdf"
            output_path = os.path.join(OUTPUT_FOLDER, output_filename)
            images_to_pdf(input_paths, output_path)
            return send_file(output_path, as_attachment=True, download_name="converted_images.pdf")
            
        if conversion_type == 'merge_pdf':
            input_paths = []
            for file in files:
                input_path = os.path.join(UPLOAD_FOLDER, f"{batch_id}_{file.filename}")
                file.save(input_path)
                input_paths.append(input_path)
            
            output_filename = f"{batch_id}_merged.pdf"
            output_path = os.path.join(OUTPUT_FOLDER, output_filename)
            merge_pdfs(input_paths, output_path)
            return send_file(output_path, as_attachment=True, download_name="merged.pdf")
            
        # Format Mapping
        format_map = {
            'to_png': ('PNG', '.png'),
            'to_jpg': ('JPEG', '.jpg'),
            'to_webp': ('WEBP', '.webp'),
            'to_gif': ('GIF', '.gif'),
            'to_bmp': ('BMP', '.bmp'),
            'to_tiff': ('TIFF', '.tiff'),
        }
            
        # Handle conversions individually
        for file in files:
            input_filename = f"{batch_id}_{file.filename}"
            input_path = os.path.join(UPLOAD_FOLDER, input_filename)
            file.save(input_path)
            
            base_name = os.path.splitext(file.filename)[0]
            
            # Map conversion type to output format (e.g., 'to_png' -> 'PNG')
            # For backward compatibility, map old values like 'jpg_to_png' to 'to_png'
            conv_key = conversion_type
            if not conversion_type.startswith('pdf_'):
                if 'to_png' in conversion_type or conversion_type == 'svg_to_png': conv_key = 'to_png'
                elif 'to_jpg' in conversion_type: conv_key = 'to_jpg'
            
            if conv_key in format_map:
                out_format, out_ext = format_map[conv_key]
                output_filename = f"{base_name}_converted{out_ext}"
                output_path = os.path.join(batch_output_dir, output_filename)
                convert_image(input_path, output_path, out_format, options)
                output_paths.append(output_path)
                
            elif conversion_type in ['pdf_to_jpg', 'pdf_to_png', 'pdf_to_webp']:
                if 'jpg' in conversion_type:
                    out_format = 'jpg'
                elif 'webp' in conversion_type:
                    out_format = 'webp'
                else:
                    out_format = 'png'
                    
                image_paths = pdf_to_images(input_path, batch_output_dir, out_format)
                output_paths.extend(image_paths)
                
            elif conversion_type == 'pdf_to_docx':
                output_filename = f"{base_name}_converted.docx"
                output_path = os.path.join(batch_output_dir, output_filename)
                pdf_to_docx_convert(input_path, output_path)
                output_paths.append(output_path)
                
            elif conversion_type == 'split_pdf':
                image_paths = split_pdf(input_path, batch_output_dir)
                output_paths.extend(image_paths)
                
            elif conversion_type == 'compress_pdf':
                output_filename = f"{base_name}_compressed.pdf"
                output_path = os.path.join(batch_output_dir, output_filename)
                compress_pdf(input_path, output_path)
                output_paths.append(output_path)
                
            elif conversion_type == 'docx_to_pdf':
                output_filename = f"{base_name}_converted.pdf"
                output_path = os.path.join(batch_output_dir, output_filename)
                docx_to_pdf_convert(input_path, output_path)
                output_paths.append(output_path)
                
            elif conversion_type == 'compress_image':
                ext = os.path.splitext(file.filename)[1].lower()
                out_format = ext[1:].upper()
                if out_format == 'JPG': out_format = 'JPEG'
                if not out_format: out_format = 'JPEG'
                output_filename = f"{base_name}_compressed{ext}"
                output_path = os.path.join(batch_output_dir, output_filename)
                convert_image(input_path, output_path, out_format, options)
                output_paths.append(output_path)
                
            else:
                return jsonify({'error': 'Invalid conversion type'}), 400
                
        # If single file output, return it directly
        if len(output_paths) == 1:
            return send_file(output_paths[0], as_attachment=True, download_name=os.path.basename(output_paths[0]))
        else:
            # Create a zip file
            zip_filename = f"converted_batch_{batch_id}.zip"
            zip_path = os.path.join(OUTPUT_FOLDER, zip_filename)
            with zipfile.ZipFile(zip_path, 'w') as zipf:
                for img_path in output_paths:
                    zipf.write(img_path, os.path.basename(img_path))
            return send_file(zip_path, as_attachment=True, download_name="converted_files.zip")
            
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("Starting Server... Open http://127.0.0.1:5000 in your browser")
    app.run(debug=True, port=5000)
