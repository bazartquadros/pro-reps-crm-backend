from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from src.models.user import db
from src.models.lead import Lead

leads_bp = Blueprint('leads', __name__)

@leads_bp.route('/leads', methods=['GET'])
@jwt_required()
def get_leads():
    leads = Lead.query.all()
    return jsonify([lead.to_dict() for lead in leads])

@leads_bp.route('/leads', methods=['POST'])
@jwt_required()
def create_lead():
    data = request.json
    lead = Lead(
        name=data['name'],
        email=data['email'],
        status=data.get('status', 'Novo'),
        source=data.get('source'),
        assigned_to=data.get('assignedTo')
    )
    db.session.add(lead)
    db.session.commit()
    return jsonify(lead.to_dict()), 201

@leads_bp.route('/leads/<int:lead_id>', methods=['PUT'])
@jwt_required()
def update_lead(lead_id):
    lead = Lead.query.get_or_404(lead_id)
    data = request.json
    
    lead.name = data.get('name', lead.name)
    lead.email = data.get('email', lead.email)
    lead.status = data.get('status', lead.status)
    lead.source = data.get('source', lead.source)
    lead.assigned_to = data.get('assignedTo', lead.assigned_to)
    
    db.session.commit()
    return jsonify(lead.to_dict())

@leads_bp.route('/leads/<int:lead_id>', methods=['DELETE'])
@jwt_required()
def delete_lead(lead_id):
    lead = Lead.query.get_or_404(lead_id)
    db.session.delete(lead)
    db.session.commit()
    return '', 204
