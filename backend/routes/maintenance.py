"""
Maintenance workflow routes.
Workflow: Pending -> Approved -> Assigned -> In Progress -> Completed -> Closed
"""

from flask import Blueprint, request, jsonify
from database import db
from models import MaintenanceRequest, Property, User, AuditLog
from routes.auth import token_required, role_required

maintenance_bp = Blueprint("maintenance", __name__)

# Valid status transitions
VALID_TRANSITIONS = {
    "pending": ["approved", "rejected"],
    "approved": ["assigned", "rejected"],
    "assigned": ["in_progress", "rejected"],
    "in_progress": ["completed"],
    "completed": ["closed"],
    "rejected": ["pending"],
    "closed": [],
}


@maintenance_bp.route("/maintenance", methods=["GET"])
@token_required
def get_maintenance_requests(current_user):
    """List maintenance requests. Staff only sees their assigned requests."""
    query = MaintenanceRequest.query

    status = request.args.get("status")
    if status:
        query = query.filter_by(status=status)

    property_id = request.args.get("property_id")
    if property_id:
        query = query.filter_by(property_id=int(property_id))

    # Staff only sees their own assigned requests + unassigned
    if current_user.role == "staff":
        query = query.filter(
            (MaintenanceRequest.assigned_to == current_user.id)
            | (MaintenanceRequest.assigned_to.is_(None))
        )

    requests_list = query.order_by(MaintenanceRequest.created_at.desc()).all()
    return jsonify({"maintenance_requests": [r.to_dict() for r in requests_list]}), 200


@maintenance_bp.route("/maintenance/<int:request_id>", methods=["GET"])
@token_required
def get_maintenance_request(current_user, request_id):
    """Get a single maintenance request."""
    req = MaintenanceRequest.query.get_or_404(request_id, description="Request not found")
    return jsonify({"maintenance_request": req.to_dict()}), 200


@maintenance_bp.route("/maintenance", methods=["POST"])
@token_required
def create_maintenance_request(current_user):
    """Create a new maintenance request."""
    data = request.get_json()

    if not data.get("property_id"):
        return jsonify({"error": "property_id is required"}), 400
    if not data.get("title"):
        return jsonify({"error": "title is required"}), 400

    prop = Property.query.get(data["property_id"])
    if not prop:
        return jsonify({"error": "Property not found"}), 404

    new_req = MaintenanceRequest(
        property_id=data["property_id"],
        title=data["title"],
        description=data.get("description", ""),
        status="pending",
    )
    db.session.add(new_req)

    audit = AuditLog(
        user_id=current_user.id,
        action=f"CREATE_MAINTENANCE: '{data['title']}' for '{prop.property_name}'",
    )
    db.session.add(audit)
    db.session.commit()

    return jsonify({"message": "Request created", "maintenance_request": new_req.to_dict()}), 201


@maintenance_bp.route("/maintenance/<int:request_id>", methods=["PUT"])
@token_required
def update_maintenance_request(current_user, request_id):
    """Update maintenance request status with workflow enforcement."""
    req = MaintenanceRequest.query.get_or_404(request_id, description="Request not found")
    data = request.get_json()
    changes = []

    if "status" in data:
        new_status = data["status"]
        old_status = req.status

        # Validate transition
        if new_status not in VALID_TRANSITIONS.get(old_status, []):
            return jsonify({"error": f"Cannot transition from '{old_status}' to '{new_status}'"}), 400

        # Role enforcement
        if new_status in ("approved", "rejected", "closed"):
            if current_user.role not in ("admin", "manager"):
                return jsonify({"error": "Only managers/admins can perform this action"}), 403

        if new_status == "assigned":
            if current_user.role not in ("admin", "manager"):
                return jsonify({"error": "Only managers/admins can assign requests"}), 403
            if not data.get("assigned_to"):
                return jsonify({"error": "assigned_to is required for assignment"}), 400
            assignee = User.query.get(data["assigned_to"])
            if not assignee:
                return jsonify({"error": "Assigned user not found"}), 404
            req.assigned_to = data["assigned_to"]

        if new_status == "approved":
            req.approved_by = current_user.id

        req.status = new_status
        changes.append(f"status: '{old_status}' -> '{new_status}'")

    if "title" in data and data["title"]:
        req.title = data["title"]
        changes.append("title updated")

    if "description" in data:
        req.description = data["description"]
        changes.append("description updated")

    if changes:
        audit = AuditLog(
            user_id=current_user.id,
            action=f"UPDATE_MAINTENANCE: Request #{request_id} - {', '.join(changes)}",
        )
        db.session.add(audit)

    db.session.commit()
    return jsonify({"message": "Request updated", "maintenance_request": req.to_dict()}), 200
