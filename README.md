# Image & PDF Converter

A beginner-friendly web application to convert between Images and PDFs, with an exact target-size compression feature.

## Project Structure
```text
image-pdf-converter/
│
├── frontend/
│   ├── index.html
│   ├── style.css
│   └── script.js
│
├── backend/
│   ├── app.py
│   ├── converter.py
│   ├── pdf_converter.py
│   ├── requirements.txt
│   ├── uploads/   (auto-created)
│   └── outputs/   (auto-created)
│
└── README.md
```

## Features

- **JPG to PNG**
- **PNG to JPG** (with Target Size in KB for compression)
- **Image to PDF**
- **PDF to JPG / PNG** (extracts pages as images and returns a ZIP if multiple pages)

## Setup Instructions

1. **Install Python** if you haven't already. (https://www.python.org/downloads/)
2. Open your terminal / command prompt.
3. Navigate to the `backend` folder:
   ```bash
   cd image-pdf-converter/backend
   ```
4. Install the required Python libraries:
   ```bash
   pip install -r requirements.txt
   ```

## How to Run

1. In the `backend` folder, start the Flask server:
   ```bash
   python app.py
   ```
2. The server will start on `http://127.0.0.1:5000`. Open this URL in your web browser.
3. You will see the beautiful frontend UI where you can upload your images and PDFs and convert them instantly!
