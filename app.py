import os
from flask import Flask, request, redirect, url_for, render_template, send_file
from werkzeug.utils import secure_filename
import pytesseract
from ultralyticsplus import YOLO
from PIL import Image
from pdf2image import convert_from_path
import numpy as np

# Configure Tesseract command if needed
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'  # Update this path if necessary

# Configure Flask app
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['CROPPED_IMAGES_FOLDER'] = 'cropped_images'
app.config['ALLOWED_EXTENSIONS'] = {'pdf'}
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['CROPPED_IMAGES_FOLDER'], exist_ok=True)

# Load YOLO model
model = YOLO('keremberke/yolov8m-table-extraction')
model.overrides['conf'] = 0.25
model.overrides['iou'] = 0.45
model.overrides['agnostic_nms'] = False
model.overrides['max_det'] = 1000

# Function to check if file is allowed
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# Function to clear files in a directory
def clear_directory(folder):
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
        except Exception as e:
            print(e)

# Route for the main page
@app.route('/')
def index():
    clear_directory(app.config['UPLOAD_FOLDER'])
    clear_directory(app.config['CROPPED_IMAGES_FOLDER'])
    return render_template('index.html')

# Route to handle file upload
@app.route('/upload', methods=['POST'])
def upload_file():
    clear_directory(app.config['UPLOAD_FOLDER'])
    clear_directory(app.config['CROPPED_IMAGES_FOLDER'])
    if 'file' not in request.files:
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        return redirect(request.url)
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        return redirect(url_for('process_file', filename=filename))
    return redirect(request.url)

# Route to process the uploaded file
@app.route('/process/<filename>')
def process_file(filename):
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    images = convert_from_path(filepath)

    extracted_tables = []
    for i, image in enumerate(images):
        # Process each page of the PDF
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], f'page_{i}.png')
        image.save(image_path)
        
        # Perform inference with YOLO to detect tables
        results = model.predict(image_path)
        
        # Extract text from each detected table and save the cropped image
        for idx, bbox in enumerate(results[0].boxes.data.numpy()):
            x1, y1, x2, y2, _, _ = map(int, bbox)
            img = np.array(image)
            cropped_image = img[y1:y2, x1:x2]
            cropped_image = Image.fromarray(cropped_image)
            cropped_image_name = f'cropped_{filename}_{idx}.png'
            cropped_image_path = os.path.join(app.config['CROPPED_IMAGES_FOLDER'], cropped_image_name)
            cropped_image.save(cropped_image_path)
            extracted_tables.append({'image_name': cropped_image_name})
    
    return render_template('result.html', tables=extracted_tables)

# Route to download the cropped table images
@app.route('/download/<path:filename>')
def download_file(filename):
    return send_file(filename, as_attachment=True)

# Run the Flask app
if __name__ == "__main__":
    app.run(debug=True)
