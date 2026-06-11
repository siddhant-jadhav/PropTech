"""
Property management routes - full CRUD with audit logging.
"""

from flask import Blueprint, request, jsonify
from database import db
from models import Property, AuditLog
from routes.auth import token_required, role_required

properties_bp = Blueprint("properties", __name__)


@properties_bp.route("/properties", methods=["GET"])
@token_required
def get_properties(current_user):
    """List all properties with optional filters."""
    query = Property.query

    city = request.args.get("city")
    if city:
        query = query.filter(Property.city.ilike(f"%{city}%"))

    status = request.args.get("status")
    if status and status in ("occupied", "vacant"):
        query = query.filter_by(occupancy_status=status)

    search = request.args.get("search")
    if search:
        query = query.filter(Property.property_name.ilike(f"%{search}%"))

    properties = query.order_by(Property.created_at.desc()).all()
    return jsonify({"properties": [p.to_dict() for p in properties]}), 200


@properties_bp.route("/properties/<int:property_id>", methods=["GET"])
@token_required
def get_property(current_user, property_id):
    """Get a single property."""
    prop = Property.query.get_or_404(property_id, description="Property not found")
    return jsonify({"property": prop.to_dict()}), 200


@properties_bp.route("/properties", methods=["POST"])
@token_required
@role_required("admin", "manager")
def create_property(current_user):
    """Create a new property."""
    data = request.get_json()

    for field in ["property_name", "city", "address"]:
        if not data.get(field):
            return jsonify({"error": f"{field} is required"}), 400

    occ_status = data.get("occupancy_status", "vacant")
    if occ_status not in ("occupied", "vacant"):
        return jsonify({"error": "Invalid occupancy_status"}), 400

    new_property = Property(
        property_name=data["property_name"],
        city=data["city"],
        address=data["address"],
        occupancy_status=occ_status,
        monthly_revenue=float(data.get("monthly_revenue", 0)),
    )
    db.session.add(new_property)

    audit = AuditLog(
        user_id=current_user.id,
        action=f"CREATE_PROPERTY: Added '{data['property_name']}' in {data['city']}",
    )
    db.session.add(audit)
    db.session.commit()

    return jsonify({"message": "Property created", "property": new_property.to_dict()}), 201


@properties_bp.route("/properties/<int:property_id>", methods=["PUT"])
@token_required
@role_required("admin", "manager")
def update_property(current_user, property_id):
    """Update a property."""
    prop = Property.query.get_or_404(property_id, description="Property not found")
    data = request.get_json()
    changes = []

    if "property_name" in data and data["property_name"]:
        changes.append(f"name: '{prop.property_name}' -> '{data['property_name']}'")
        prop.property_name = data["property_name"]

    if "city" in data and data["city"]:
        changes.append(f"city: '{prop.city}' -> '{data['city']}'")
        prop.city = data["city"]

    if "address" in data and data["address"]:
        prop.address = data["address"]
        changes.append("address updated")

    if "occupancy_status" in data:
        if data["occupancy_status"] in ("occupied", "vacant"):
            changes.append(f"status: '{prop.occupancy_status}' -> '{data['occupancy_status']}'")
            prop.occupancy_status = data["occupancy_status"]

    if "monthly_revenue" in data:
        changes.append(f"revenue: {prop.monthly_revenue} -> {data['monthly_revenue']}")
        prop.monthly_revenue = float(data["monthly_revenue"])

    if changes:
        audit = AuditLog(
            user_id=current_user.id,
            action=f"UPDATE_PROPERTY: Updated #{property_id} - {', '.join(changes)}",
        )
        db.session.add(audit)
    db.session.commit()

    return jsonify({"message": "Property updated", "property": prop.to_dict()}), 200


@properties_bp.route("/properties/<int:property_id>", methods=["DELETE"])
@token_required
@role_required("admin")
def delete_property(current_user, property_id):
    """Delete a property (admin only)."""
    prop = Property.query.get_or_404(property_id, description="Property not found")
    name = prop.property_name

    db.session.delete(prop)
    audit = AuditLog(
        user_id=current_user.id,
        action=f"DELETE_PROPERTY: Deleted '{name}' (ID: {property_id})",
    )
    db.session.add(audit)
    db.session.commit()

    return jsonify({"message": f"Property '{name}' deleted"}), 200
