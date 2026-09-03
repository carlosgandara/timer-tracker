import os
from dotenv import load_dotenv

load_dotenv()  # Must be here

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")
    # Use the environment variable, fallback to SQLite only if not set
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///instance/colors.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG = True