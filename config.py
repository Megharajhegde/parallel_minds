import os

class Config:
    # Use an absolute path for the SQLite database
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.join(BASE_DIR, 'library.db')}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024 # Limit uploads to 16MB