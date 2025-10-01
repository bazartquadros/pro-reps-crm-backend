from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from src.models.user import db
from src.models.sale import Sale

sales_bp = Blueprint('sales', __name__)

@sales_bp.route('/sales', methods=['GET'])
@jwt_required()
def get_sales():
    sales = Sale.query.all()
    return jsonify([sale.to_dict() for sale in sales])

@sales_bp.route('/sales', methods=['POST'])
@jwt_required()
def create_sale():
    data = request.json
    sale = Sale(
        client_id=data['clientId'],
        client_name=data['clientName'],
        product=data['product'],
        value=data['value'],
        status=data.get('status', 'Pendente'),
        representative=data['representative']
    )
    db.session.add(sale)
    db.session.commit()
    return jsonify(sale.to_dict()), 201

@sales_bp.route('/sales/<int:sale_id>', methods=['PUT'])
@jwt_required()
def update_sale(sale_id):
    sale = Sale.query.get_or_404(sale_id)
    data = request.json
    
    sale.client_name = data.get('clientName', sale.client_name)
    sale.product = data.get('product', sale.product)
    sale.value = data.get('value', sale.value)
    sale.status = data.get('status', sale.status)
    sale.representative = data.get('representative', sale.representative)
    
    db.session.commit()
    return jsonify(sale.to_dict())

@sales_bp.route('/sales/<int:sale_id>', methods=['DELETE'])
@jwt_required()
def delete_sale(sale_id):
    sale = Sale.query.get_or_404(sale_id)
    db.session.delete(sale)
    db.session.commit()
    return '', 204
