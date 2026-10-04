import os
import io
from PIL import Image, ImageOps
import pillow_heif
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPM

# Register HEIF opener
pillow_heif.register_heif_opener()

def convert_image(input_path, output_path, output_format, options=None):
    if options is None:
        options = {}
        
    # Handle SVG separately because it's a vector format
    if input_path.lower().endswith('.svg') and output_format.lower() in ['png', 'jpeg', 'jpg']:
        drawing = svg2rlg(input_path)
        # Render to a temporary PNG first, then open with PIL to apply options
        temp_io = io.BytesIO()
        renderPM.drawToFile(drawing, temp_io, fmt="PNG")
        temp_io.seek(0)
        img = Image.open(temp_io)
    else:
        img = Image.open(input_path)
    
    # Handle EXIF orientation
    img = ImageOps.exif_transpose(img)
    
    # 1. Flip
    if options.get('flip_h') == 'true':
        img = img.transpose(Image.FLIP_LEFT_RIGHT)
    if options.get('flip_v') == 'true':
        img = img.transpose(Image.FLIP_TOP_BOTTOM)
        
    # 2. Rotate
    rotate_deg = options.get('rotate')
    if rotate_deg and rotate_deg != '0':
        img = img.rotate(-int(rotate_deg), expand=True) # Negative to rotate clockwise
        
    # 3. Resize
    width = options.get('width')
    height = options.get('height')
    if width and height:
        try:
            img = img.resize((int(width), int(height)), Image.Resampling.LANCZOS)
        except ValueError:
            pass
            
    # Convert RGBA to RGB if output format doesn't support alpha
    if output_format.lower() in ['jpeg', 'jpg', 'bmp'] and img.mode in ('RGBA', 'P', 'LA'):
        img = img.convert('RGB')
        
    # Check target size for JPEG
    target_size_kb = options.get('target_size')
    quality = options.get('quality', 80)
    
    if target_size_kb and output_format.lower() in ['jpeg', 'jpg']:
        # Binary search for quality to match target size
        min_q = 1
        max_q = 100
        best_q = 50
        target_bytes = float(target_size_kb) * 1024
        
        while min_q <= max_q:
            mid_q = (min_q + max_q) // 2
            temp_io = io.BytesIO()
            img.save(temp_io, format='JPEG', quality=mid_q)
            size = temp_io.tell()
            
            if size <= target_bytes:
                best_q = mid_q
                min_q = mid_q + 1
            else:
                max_q = mid_q - 1
                
        img.save(output_path, format='JPEG', quality=best_q)
    else:
        # Save normally using quality if it's JPEG or WEBP
        save_kwargs = {'format': output_format.upper()}
        if output_format.lower() in ['jpeg', 'jpg', 'webp']:
            try:
                save_kwargs['quality'] = int(quality)
            except ValueError:
                save_kwargs['quality'] = 80
                
        img.save(output_path, **save_kwargs)
