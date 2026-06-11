"""
Authentication & User Management routes.
Provides JWT login plus full CRUD for user administration.
"""

from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime
from functools import wraps
from database import db
from models import User, AuditLog
from config import Config

auth_bp = Blueprint("auth", __name__)


# ---- Decorators ----

def token_required(f):
    """Protect routes with JWT authentication."""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if "Authorization" in request.headers:
            auth_header = request.headers["Authorization"]
            if auth_header.startswith("Bearer "):
                token = auth_header.split(" ")[1]

        if not token:
            return jsonify({"error": "Authentication token is missing"}), 401

        try:
            payload = jwt.decode(token, Config.JWT_SECRET_KEY, algorithms=["HS256"])
            current_user = User.query.get(payload["user_id"])
            if not current_user:
                return jsonify({"error": "User not found"}), 401
            if current_user.status == "inactive":
                return jsonify({"error": "Account is inactive"}), 403
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token has expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid token"}), 401

        return f(current_user, *args, **kwargs)
    return decorated


def role_required(*roles):
    """Enforce role-based access control."""
    def decorator(f):
        @wraps(f)
        def decorated(current_user, *args, **kwargs):
            if current_user.role not in roles:
                return jsonify({"error": "Insufficient permissions"}), 403
            return f(current_user, *args, **kwargs)
        return decorated
    return decorator


# ---- Auth Endpoints ----

@auth_bp.route("/login", methods=["POST"])
def login():
    """Authenticate user and return JWT token."""
    data = request.get_json()
    if not data or not data.get("email") or not data.get("password"):
        return jsonify({"error": "Email and password are required"}), 400

    user = User.query.filter_by(email=data["email"]).first()
    if not user or not check_password_hash(user.password_hash, data["password"]):
        return jsonify({"error": "Invalid email or password"}), 401

    if user.status == "inactive":
        return jsonify({"error": "Account is inactive. Contact your administrator."}), 403

    token_payload = {
        "user_id": user.id,
        "email": user.email,
        "role": user.role,
        "exp": datetime.datetime.utcnow() + Config.JWT_ACCESS_TOKEN_EXPIRES,
        "iat": datetime.datetime.utcnow(),
    }
    token = jwt.encode(token_payload, Config.JWT_SECRET_KEY, algorithm="HS256")

    audit = AuditLog(user_id=user.id, action=f"LOGIN: {user.name} logged in")
    db.session.add(audit)
    db.session.commit()

    return jsonify({"token": token, "user": user.to_dict()}), 200


@auth_bp.route("/profile", methods=["GET"])
@token_required
def get_profile(current_user):
    """Get current user profile."""
    return jsonify({"user": current_user.to_dict()}), 200


# ---- User Management Endpoints (Admin Only) ----

@auth_bp.route("/users", methods=["GET"])
@token_required
@role_required("admin", "manager")
def get_users(current_user):
    """List all users."""
    users = User.query.order_by(User.created_at.desc()).all()
    return jsonify({"users": [u.to_dict() for u in users]}), 200


@auth_bp.route("/users", methods=["POST"])
@token_required
@role_required("admin")
def create_user(current_user):
    """Create a new user (admin only)."""
    data = request.get_json()

    required = ["name", "email", "password", "role"]
    for field in required:
        if not data.get(field):
            return jsonify({"error": f"{field} is required"}), 400

    if data["role"] not in ("admin", "manager", "staff"):
        return jsonify({"error": "Invalid role"}), 400

    if User.query.filter_by(email=data["email"]).first():
        return jsonify({"error": "Email already registered"}), 409

    new_user = User(
        name=data["name"],
        email=data["email"],
        password_hash=generate_password_hash(data["password"]),
        role=data["role"],
        status=data.get("status", "active"),
    )
    db.session.add(new_user)

    audit = AuditLog(
        user_id=current_user.id,
        action=f"CREATE_USER: Created {data['name']} ({data['role']})",
    )
    db.session.add(audit)
    db.session.commit()

    return jsonify({"message": "User created", "user": new_user.to_dict()}), 201


@auth_bp.route("/users/<int:user_id>", methods=["PUT"])
@token_required
@role_required("admin")
def update_user(current_user, user_id):
    """Update an existing user (admin only)."""
    user = User.query.get_or_404(user_id, description="User not found")
    data = request.get_json()
    changes = []

    if "name" in data and data["name"]:
        changes.append(f"name: '{user.name}' -> '{data['name']}'")
        user.name = data["name"]

    if "email" in data and data["email"]:
        existing = User.query.filter(User.email == data["email"], User.id != user_id).first()
        if existing:
            return jsonify({"error": "Email already in use"}), 409
        changes.append(f"email updated")
        user.email = data["email"]

    if "role" in data and data["role"] in ("admin", "manager", "staff"):
        changes.append(f"role: '{user.role}' -> '{data['role']}'")
        user.role = data["role"]

    if "status" in data and data["status"] in ("active", "inactive"):
        changes.append(f"status: '{user.status}' -> '{data['status']}'")
        user.status = data["status"]

    if "password" in data and data["password"]:
        user.password_hash = generate_password_hash(data["password"])
        changes.append("password changed")

    if changes:
        audit = AuditLog(
            user_id=current_user.id,
            action=f"UPDATE_USER: Updated user #{user_id} - {', '.join(changes)}",
        )
        db.session.add(audit)

    db.session.commit()
    return jsonify({"message": "User updated", "user": user.to_dict()}), 200


@auth_bp.route("/users/<int:user_id>", methods=["DELETE"])
@token_required
@role_required("admin")
def delete_user(current_user, user_id):
    """Delete a user (admin only). Cannot delete self."""
    if current_user.id == user_id:
        return jsonify({"error": "Cannot delete your own account"}), 400

    user = User.query.get_or_404(user_id, description="User not found")
    user_name = user.name

    db.session.delete(user)
    audit = AuditLog(
        user_id=current_user.id,
        action=f"DELETE_USER: Deleted '{user_name}' (ID: {user_id})",
    )
    db.session.add(audit)
    db.session.commit()

    return jsonify({"message": f"User '{user_name}' deleted"}), 200
