import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-here')
    CHROMA_DB_PATH = "./chroma_db"