import os
import sys

# Adiciona o diretório com as bibliotecas ao path do Python
sys.path.insert(0, '.\u200b')  # Diretório com zero-width space
sys.path.insert(0, '.')

from flask import Flask, render_template, request, send_file
import os
import pandas as pd
from utils.classifier import process_csv
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

# Ensure directories exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['PROCESSED_FOLDER'], exist_ok=True)

def allowed_file(filename):
    return Config.is_allowed_file(filename)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/health')
def health_check():
    return {'status': 'healthy', 'message': 'Application is running'}, 200

@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        if 'file' not in request.files:
            return "No file part", 400
        file = request.files['file']
        if file.filename == '':
            return "No selected file", 400
        if file and allowed_file(file.filename):
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(filepath)
            output_file = process_csv(filepath)
            return send_file(output_file, as_attachment=True)
        else:
            return "Invalid file type. Please upload a CSV file.", 400
    except Exception as e:
        app.logger.error(f"Error processing file: {str(e)}")
        return f"Error processing file: {str(e)}", 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)