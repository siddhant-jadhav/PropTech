"""
Database initialization module.
Sets up SQLAlchemy engine and session management.
"""

from flask_sqlalchemy import SQLAlchemy

# Global SQLAlchemy instance - initialized with Flask app in app.py
db = SQLAlchemy()


def init_db(app):
    """
    Initialize the database with the Flask application.
    Creates all tables if they don't exist.

    Args:
        app: Flask application instance
    """
    db.init_app(app)
    with app.app_context():
        # Import models to register them with SQLAlchemy
        import models  # noqa: F401
        db.create_all()
