import requests
import os

url = 'http://127.0.0.1:5000/api/convert'

with open('dummy.jpg', 'wb') as f:
    f.write(b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00\xff\xdb\x00C\x00\x08\x06\x06\x07\x06\x05\x08\x07\x07\x07\t\t\x08\n\x0c\x14\r\x0c\x0b\x0b\x0c\x19\x12\x13\x0f\x14\x1d\x1a\x1f\x1e\x1d\x1a\x1c\x1c $.\' \",#\x1c\x1c(7),01444\x1f\'9=82<.342\xff\xc0\x00\x0b\x08\x00\x01\x00\x01\x01\x01\x11\x00\xff\xc4\x00\x1f\x00\x00\x01\x05\x01\x01\x01\x01\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x0b\xff\xda\x00\x08\x01\x01\x00\x00\x3f\x00\xfd\xfc')

# Test Image to PNG
r = requests.post(url, files={'file': open('dummy.jpg', 'rb')}, data={'conversion_type': 'to_png'})
print('to_png:', r.status_code)

# Test Image to PDF
r = requests.post(url, files={'file': open('dummy.jpg', 'rb')}, data={'conversion_type': 'image_to_pdf'})
print('image_to_pdf:', r.status_code)

# Test PDF to JPG
r = requests.post(url, files={'file': open('dummy.pdf', 'rb')}, data={'conversion_type': 'pdf_to_jpg'})
print('pdf_to_jpg:', r.status_code)

# Test Split PDF
r = requests.post(url, files={'file': open('dummy.pdf', 'rb')}, data={'conversion_type': 'split_pdf'})
print('split_pdf:', r.status_code)
