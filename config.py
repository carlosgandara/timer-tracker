import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")
    # Use an absolute path with forward slashes
    SQLALCHEMY_DATABASE_URI = "sqlite:///C:/Users/user1/Desktop/colorApp/colors.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG = True