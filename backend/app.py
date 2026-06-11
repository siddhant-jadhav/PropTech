"""
Property Management System - Flask Backend
"""

import os
import time
from flask import Flask, jsonify
from flask_cors import CORS
from werkzeug.security import generate_password_hash
from config import Config
from database import db, init_db

from routes.auth import auth_bp
from routes.properties import properties_bp
from routes.maintenance import maintenance_bp
from routes.reports import reports_bp
from routes.dashboard import dashboard_bp


def create_app():
    """Application factory."""
    app = Flask(__name__)
    app.config.from_object(Config)

    CORS(app, resources={r"/*": {"origins": "*"}})
    init_db(app)

    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(properties_bp)
    app.register_blueprint(maintenance_bp)
    app.register_blueprint(reports_bp)
    app.register_blueprint(dashboard_bp)

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({"error": "Resource not found"}), 404

    @app.errorhandler(405)
    def method_not_allowed(error):
        return jsonify({"error": "Method not allowed"}), 405

    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({"error": "Internal server error"}), 500

    @app.route("/", methods=["GET"])
    def index():
        return jsonify({
            "application": "Property Management System API",
            "version": "2.0.0",
            "status": "running",
        }), 200

    return app


def wait_for_db(app, max_retries=30, delay=2):
    """Wait for MySQL to be ready before starting."""
    with app.app_context():
        for attempt in range(max_retries):
            try:
                db.session.execute(db.text("SELECT 1"))
                print(f"[OK] Database connected on attempt {attempt + 1}")
                return True
            except Exception as e:
                print(f"[WAIT] Database not ready... attempt {attempt + 1}/{max_retries}")
                time.sleep(delay)
        print("[FAIL] Could not connect to database")
        return False


def seed_passwords(app):
    """Fix seed user passwords on startup."""
    from models import User
    with app.app_context():
        users = User.query.all()
        for user in users:
            if user.password_hash == "placeholder" or not user.password_hash.startswith("scrypt:") and not user.password_hash.startswith("pbkdf2:"):
                user.password_hash = generate_password_hash("Password@123")
        db.session.commit()
        print(f"[OK] Password hashes verified for {len(users)} users")


if __name__ == "__main__":
    app = create_app()
    if wait_for_db(app):
        seed_passwords(app)
        app.run(
            host=os.getenv("FLASK_HOST", "0.0.0.0"),
            port=int(os.getenv("FLASK_PORT", 5000)),
            debug=Config.DEBUG,
        )
    else:
        exit(1)
