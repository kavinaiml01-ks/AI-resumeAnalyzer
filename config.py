import os
import urllib.parse

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    """
    Central configuration for the SmartHire AI application.
    Uses MySQL when DB connection details are provided; otherwise falls back to SQLite.
    """

    SECRET_KEY = os.environ.get("SECRET_KEY", "smarthire-ai-secret-key-change-me")

    DB_USER = os.environ.get("DB_USER", "").strip()
    DB_PASSWORD_RAW = os.environ.get("DB_PASSWORD", "").strip()
    DB_PASSWORD = urllib.parse.quote_plus(DB_PASSWORD_RAW) if DB_PASSWORD_RAW else ""
    DB_HOST = os.environ.get("DB_HOST", "").strip()
    DB_PORT = os.environ.get("DB_PORT", "3306").strip()
    DB_NAME = os.environ.get("DB_NAME", "smarthire_ai").strip()

    if DB_HOST and DB_USER and DB_NAME:
        SQLALCHEMY_DATABASE_URI = (
            f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
        )
    else:
        sqlite_path = os.path.join(BASE_DIR, "app.db")
        SQLALCHEMY_DATABASE_URI = f"sqlite:///{sqlite_path}"

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
    ALLOWED_EXTENSIONS = {"pdf"}
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  

    JOBS_PER_PAGE = 8
