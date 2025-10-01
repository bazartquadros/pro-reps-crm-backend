from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.models.user import User, db
from src.models.customer import Customer

customers_bp = Blueprint('customers', __name__)

@customers_bp.route('/customers', methods=['GET'])
@jwt_required()
def get_customers():
    """Lista todos os clientes"""
    customers = Customer.query.all()
    return jsonify([customer.to_dict() for customer in customers])

@customers_bp.route('/customers', methods=['POST'])
@jwt_required()
def create_customer():
    """Cria novo cliente"""
    data = request.json
    
    # Validações
    if not data.get('name') or not data.get('email'):
        return jsonify({'error': 'Nome e email são obrigatórios'}), 400
    
    customer = Customer(
        name=data['name'],
        email=data['email'],
        phone=data.get('phone'),
        company=data.get('company')
    )
    
    db.session.add(customer)
    db.session.commit()
    
    return jsonify(customer.to_dict()), 201

@customers_bp.route('/customers/<int:customer_id>', methods=['GET'])
@jwt_required()
def get_customer(customer_id):
    """Retorna cliente específico"""
    customer = Customer.query.get_or_404(customer_id)
    return jsonify(customer.to_dict())

@customers_bp.route('/customers/<int:customer_id>', methods=['PUT'])
@jwt_required()
def update_customer(customer_id):
    """Atualiza cliente"""
    customer = Customer.query.get_or_404(customer_id)
    data = request.json
    
    customer.name = data.get('name', customer.name)
    customer.email = data.get('email', customer.email)
    customer.phone = data.get('phone', customer.phone)
    customer.company = data.get('company', customer.company)
    
    db.session.commit()
    return jsonify(customer.to_dict())

@customers_bp.route('/customers/<int:customer_id>', methods=['DELETE'])
@jwt_required()
def delete_customer(customer_id):
    """Exclui cliente"""
    customer = Customer.query.get_or_404(customer_id)
    db.session.delete(customer)
    db.session.commit()
    
    return '', 204
