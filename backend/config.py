"""
Configuration module for the Flask backend.
Loads environment variables and provides configuration classes.
"""

import os
from datetime import timedelta
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Base configuration class."""

    # Flask settings
    SECRET_KEY = os.getenv("FLASK_SECRET_KEY", "default-secret-key-change-in-production")
    DEBUG = os.getenv("FLASK_DEBUG", "0") == "1"

    # MySQL Database settings
    MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
    MYSQL_PORT = int(os.getenv("MYSQL_PORT", 3306))
    MYSQL_USER = os.getenv("MYSQL_USER", "proptech_user")
    MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "PropUser@2024!")
    MYSQL_DATABASE = os.getenv("MYSQL_DATABASE", "property_management")

    # SQLAlchemy database URI
    SQLALCHEMY_DATABASE_URI = (
        f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}"
        f"@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_size": 10,
        "pool_recycle": 3600,
        "pool_pre_ping": True,
        "max_overflow": 20,
    }

    # JWT settings
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "default-jwt-secret")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(
        seconds=int(os.getenv("JWT_ACCESS_TOKEN_EXPIRES", 3600))
    )
