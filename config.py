import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your_secret_key_here'
    UPLOAD_FOLDER = 'uploads'
    PROCESSED_FOLDER = 'processed'
    ALLOWED_EXTENSIONS = {'csv'}

    @staticmethod
    def is_allowed_file(filename):
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS