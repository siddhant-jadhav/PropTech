"""
Dashboard & Health check routes.
"""

from flask import Blueprint, jsonify
import psutil
from sqlalchemy import func
from database import db
from models import Property, MaintenanceRequest, AuditLog
from routes.auth import token_required

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/dashboard", methods=["GET"])
@token_required
def get_dashboard(current_user):
    """Dashboard KPIs, chart data, and recent activity."""

    # Property stats
    total_properties = Property.query.count()
    occupied = Property.query.filter_by(occupancy_status="occupied").count()
    vacant = Property.query.filter_by(occupancy_status="vacant").count()

    # Revenue stats
    total_revenue = float(db.session.query(func.sum(Property.monthly_revenue)).scalar() or 0)
    avg_revenue = float(db.session.query(func.avg(Property.monthly_revenue)).scalar() or 0)

    # Maintenance stats
    total_maintenance = MaintenanceRequest.query.count()
    pending = MaintenanceRequest.query.filter_by(status="pending").count()
    in_progress = MaintenanceRequest.query.filter_by(status="in_progress").count()
    completed = MaintenanceRequest.query.filter_by(status="completed").count()
    assigned = MaintenanceRequest.query.filter_by(status="assigned").count()

    # Chart data
    city_distribution = (
        db.session.query(Property.city, func.count(Property.id).label("count"))
        .group_by(Property.city)
        .order_by(func.count(Property.id).desc())
        .all()
    )
    revenue_by_city = (
        db.session.query(Property.city, func.sum(Property.monthly_revenue).label("revenue"))
        .group_by(Property.city)
        .order_by(func.sum(Property.monthly_revenue).desc())
        .all()
    )

    # Recent activity
    recent_logs = AuditLog.query.order_by(AuditLog.timestamp.desc()).limit(10).all()

    return jsonify({
        "kpis": {
            "total_properties": total_properties,
            "occupied_properties": occupied,
            "vacant_properties": vacant,
            "occupancy_rate": round((occupied / total_properties) * 100, 1) if total_properties > 0 else 0,
            "total_monthly_revenue": total_revenue,
            "avg_revenue_per_property": round(avg_revenue, 2),
            "annual_projected_revenue": total_revenue * 12,
        },
        "maintenance": {
            "total": total_maintenance,
            "pending": pending,
            "assigned": assigned,
            "in_progress": in_progress,
            "completed": completed,
        },
        "charts": {
            "city_distribution": [{"city": r.city, "count": r.count} for r in city_distribution],
            "revenue_by_city": [{"city": r.city, "revenue": float(r.revenue or 0)} for r in revenue_by_city],
        },
        "recent_activity": [log.to_dict() for log in recent_logs],
    }), 200


@dashboard_bp.route("/health", methods=["GET"])
def health_check():
    """Health check with system resource metrics."""
    db_status = "healthy"
    try:
        db.session.execute(db.text("SELECT 1"))
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"

    cpu = psutil.cpu_percent(interval=0.5)
    mem = psutil.virtual_memory()
    disk = psutil.disk_usage("/")

    return jsonify({
        "status": "running",
        "database": db_status,
        "system": {
            "cpu_usage_percent": cpu,
            "ram_total_gb": round(mem.total / (1024 ** 3), 2),
            "ram_used_gb": round(mem.used / (1024 ** 3), 2),
            "ram_usage_percent": mem.percent,
            "disk_total_gb": round(disk.total / (1024 ** 3), 2),
            "disk_used_gb": round(disk.used / (1024 ** 3), 2),
            "disk_usage_percent": round(disk.percent, 1),
        },
    }), 200
