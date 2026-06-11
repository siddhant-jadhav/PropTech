"""
SQLAlchemy ORM Models for the Property Management System.
"""

from datetime import datetime
from database import db


class User(db.Model):
    """User model with role-based access and status tracking."""

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), nullable=False, unique=True, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.Enum("admin", "manager", "staff"), nullable=False, default="staff")
    status = db.Column(db.Enum("active", "inactive"), nullable=False, default="active")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    audit_logs = db.relationship("AuditLog", backref="user", lazy="dynamic")

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "role": self.role,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class Property(db.Model):
    """Property model for managing real estate assets."""

    __tablename__ = "properties"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    property_name = db.Column(db.String(200), nullable=False)
    city = db.Column(db.String(100), nullable=False, index=True)
    address = db.Column(db.Text, nullable=False)
    occupancy_status = db.Column(
        db.Enum("occupied", "vacant"), nullable=False, default="vacant"
    )
    monthly_revenue = db.Column(db.Numeric(12, 2), nullable=False, default=0.00)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    maintenance_requests = db.relationship(
        "MaintenanceRequest", backref="property", lazy="dynamic", cascade="all, delete-orphan"
    )

    def to_dict(self):
        return {
            "id": self.id,
            "property_name": self.property_name,
            "city": self.city,
            "address": self.address,
            "occupancy_status": self.occupancy_status,
            "monthly_revenue": float(self.monthly_revenue),
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class MaintenanceRequest(db.Model):
    """Maintenance request model with full workflow status tracking."""

    __tablename__ = "maintenance_requests"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    property_id = db.Column(
        db.Integer, db.ForeignKey("properties.id", ondelete="CASCADE"), nullable=False
    )
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    status = db.Column(
        db.Enum("pending", "approved", "assigned", "in_progress", "completed", "closed", "rejected"),
        nullable=False,
        default="pending",
    )
    assigned_to = db.Column(
        db.Integer, db.ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    approved_by = db.Column(
        db.Integer, db.ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    assignee = db.relationship("User", foreign_keys=[assigned_to], backref="assigned_requests")
    approver = db.relationship("User", foreign_keys=[approved_by], backref="approved_requests")

    def to_dict(self):
        return {
            "id": self.id,
            "property_id": self.property_id,
            "property_name": self.property.property_name if self.property else None,
            "title": self.title,
            "description": self.description,
            "status": self.status,
            "assigned_to": self.assigned_to,
            "assigned_to_name": self.assignee.name if self.assignee else None,
            "approved_by": self.approved_by,
            "approved_by_name": self.approver.name if self.approver else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class AuditLog(db.Model):
    """Immutable audit log for all CRUD operations."""

    __tablename__ = "audit_logs"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    action = db.Column(db.String(500), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "user_name": self.user.name if self.user else "System",
            "action": self.action,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
        }
