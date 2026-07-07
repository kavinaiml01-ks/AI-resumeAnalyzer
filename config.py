import os
import urllib.parse

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    """
    Central configuration for the SmartHire AI application.
    Update the DB_* values below to match your local MySQL setup.
    """

    SECRET_KEY = os.environ.get("SECRET_KEY", "smarthire-ai-secret-key-change-me")

    # ---- MySQL Database Settings ----
    DB_USER = os.environ.get("DB_USER", "root")
    DB_PASSWORD_RAW = os.environ.get("DB_PASSWORD", "kavin@123")
    DB_PASSWORD = urllib.parse.quote_plus(DB_PASSWORD_RAW)
    DB_HOST = os.environ.get("DB_HOST", "localhost")
    DB_PORT = os.environ.get("DB_PORT", "3306")
    DB_NAME = os.environ.get("DB_NAME", "smarthire_ai")

    SQLALCHEMY_DATABASE_URI = (
        f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # ---- File Upload Settings ----
    UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
    ALLOWED_EXTENSIONS = {"pdf"}
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5 MB max resume size

    # ---- Pagination ----
    JOBS_PER_PAGE = 8
