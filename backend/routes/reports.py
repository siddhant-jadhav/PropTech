"""
Reporting routes - occupancy, revenue, and maintenance analytics.
"""

from flask import Blueprint, request, jsonify
from sqlalchemy import func
from database import db
from models import Property, MaintenanceRequest, AuditLog
from routes.auth import token_required, role_required

reports_bp = Blueprint("reports", __name__)


@reports_bp.route("/reports", methods=["GET"])
@token_required
@role_required("admin", "manager")
def get_reports(current_user):
    """Generate reports by type (occupancy, revenue, maintenance, or all)."""
    report_type = request.args.get("type", "all")
    result = {}

    if report_type in ("occupancy", "all"):
        result["occupancy_report"] = _occupancy_report()
    if report_type in ("revenue", "all"):
        result["revenue_report"] = _revenue_report()
    if report_type in ("maintenance", "all"):
        result["maintenance_report"] = _maintenance_report()

    audit = AuditLog(
        user_id=current_user.id,
        action=f"GENERATE_REPORT: {report_type} report",
    )
    db.session.add(audit)
    db.session.commit()

    return jsonify(result), 200


def _occupancy_report():
    total = Property.query.count()
    occupied = Property.query.filter_by(occupancy_status="occupied").count()
    vacant = Property.query.filter_by(occupancy_status="vacant").count()

    city_stats = (
        db.session.query(
            Property.city,
            func.count(Property.id).label("total"),
            func.sum(db.case((Property.occupancy_status == "occupied", 1), else_=0)).label("occupied"),
            func.sum(db.case((Property.occupancy_status == "vacant", 1), else_=0)).label("vacant"),
        )
        .group_by(Property.city)
        .all()
    )

    return {
        "total_properties": total,
        "occupied": occupied,
        "vacant": vacant,
        "occupancy_rate": round((occupied / total) * 100, 1) if total > 0 else 0,
        "city_breakdown": [
            {
                "city": r.city,
                "total": r.total,
                "occupied": int(r.occupied or 0),
                "vacant": int(r.vacant or 0),
                "occupancy_rate": round((int(r.occupied or 0) / r.total) * 100, 1) if r.total > 0 else 0,
            }
            for r in city_stats
        ],
    }


def _revenue_report():
    total_revenue = float(db.session.query(func.sum(Property.monthly_revenue)).scalar() or 0)

    city_revenue = (
        db.session.query(
            Property.city,
            func.sum(Property.monthly_revenue).label("total_revenue"),
            func.avg(Property.monthly_revenue).label("avg_revenue"),
            func.count(Property.id).label("property_count"),
        )
        .group_by(Property.city)
        .order_by(func.sum(Property.monthly_revenue).desc())
        .all()
    )

    top_properties = (
        Property.query.filter(Property.monthly_revenue > 0)
        .order_by(Property.monthly_revenue.desc())
        .limit(5)
        .all()
    )

    return {
        "total_monthly_revenue": total_revenue,
        "annual_projected_revenue": total_revenue * 12,
        "city_breakdown": [
            {
                "city": r.city,
                "total_revenue": float(r.total_revenue or 0),
                "avg_revenue": round(float(r.avg_revenue or 0), 2),
                "property_count": r.property_count,
            }
            for r in city_revenue
        ],
        "top_properties": [p.to_dict() for p in top_properties],
    }


def _maintenance_report():
    total = MaintenanceRequest.query.count()

    status_counts = (
        db.session.query(
            MaintenanceRequest.status,
            func.count(MaintenanceRequest.id).label("count"),
        )
        .group_by(MaintenanceRequest.status)
        .all()
    )
    status_breakdown = {r.status: r.count for r in status_counts}

    property_maintenance = (
        db.session.query(
            Property.property_name,
            func.count(MaintenanceRequest.id).label("request_count"),
        )
        .join(MaintenanceRequest, MaintenanceRequest.property_id == Property.id)
        .group_by(Property.property_name)
        .order_by(func.count(MaintenanceRequest.id).desc())
        .all()
    )

    return {
        "total_requests": total,
        "status_breakdown": status_breakdown,
        "pending": status_breakdown.get("pending", 0),
        "in_progress": status_breakdown.get("in_progress", 0),
        "completed": status_breakdown.get("completed", 0),
        "closed": status_breakdown.get("closed", 0),
        "completion_rate": round((status_breakdown.get("completed", 0) / total) * 100, 1) if total > 0 else 0,
        "property_breakdown": [
            {"property_name": r.property_name, "request_count": r.request_count}
            for r in property_maintenance
        ],
    }
