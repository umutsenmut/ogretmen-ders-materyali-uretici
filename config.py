import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-change-in-production")
    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "static", "uploads")
    ALLOWED_EXTENSIONS = {"pdf", "docx", "xlsx", "xls"}
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10 MB
    DATABASE_PATH = os.path.join(os.path.dirname(__file__), "materials.db")
    OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
    GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
