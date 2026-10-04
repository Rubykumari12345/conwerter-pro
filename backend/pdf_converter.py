import fitz # PyMuPDF
import img2pdf
from PIL import Image
import os
from pdf2docx import Converter

def pdf_to_images(pdf_path, output_dir, output_format='png'):
    doc = fitz.open(pdf_path)
    image_paths = []
    
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        pix = page.get_pixmap(dpi=150) # Set reasonable DPI
        
        output_path = os.path.join(output_dir, f"page_{page_num + 1}.{output_format}")
        
        # PyMuPDF might not natively save to WEBP depending on the version
        # It's safer to convert via PIL for webp
        if output_format == 'webp':
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            img.save(output_path, "WEBP")
        else:
            pix.save(output_path)
            
        image_paths.append(output_path)
        
    return image_paths

def images_to_pdf(image_paths, output_pdf_path):
    # Convert images to PDF using img2pdf
    with open(output_pdf_path, "wb") as f:
        f.write(img2pdf.convert(image_paths))

def pdf_to_docx_convert(pdf_path, output_docx_path):
    cv = Converter(pdf_path)
    cv.convert(output_docx_path, start=0, end=None)
    cv.close()
    return output_docx_path

def merge_pdfs(pdf_paths, output_path):
    result = fitz.open()
    for pdf in pdf_paths:
        with fitz.open(pdf) as mfile:
            result.insert_pdf(mfile)
    result.save(output_path)
    result.close()
    return output_path

def split_pdf(pdf_path, output_dir):
    doc = fitz.open(pdf_path)
    output_paths = []
    base = os.path.basename(pdf_path).replace('.pdf', '')
    for i in range(len(doc)):
        new_doc = fitz.open()
        new_doc.insert_pdf(doc, from_page=i, to_page=i)
        out_name = os.path.join(output_dir, f"{base}_page_{i+1}.pdf")
        new_doc.save(out_name)
        new_doc.close()
        output_paths.append(out_name)
    doc.close()
    return output_paths

def compress_pdf(pdf_path, output_path):
    doc = fitz.open(pdf_path)
    doc.save(output_path, garbage=4, deflate=True, clean=True)
    doc.close()
    return output_path

def docx_to_pdf_convert(docx_path, output_path):
    from docx2pdf import convert as docx2pdf_convert
    docx2pdf_convert(docx_path, output_path)
    return output_path
