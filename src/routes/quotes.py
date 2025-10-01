from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.models.user import User, db
from src.models.quote import Quote
from datetime import datetime

quotes_bp = Blueprint('quotes', __name__)

@quotes_bp.route('/quotes', methods=['GET'])
@jwt_required()
def get_quotes():
    """Lista todas as cotações"""
    quotes = Quote.query.order_by(Quote.created_at.desc()).all()
    return jsonify([quote.to_dict() for quote in quotes])

@quotes_bp.route('/quotes', methods=['POST'])
@jwt_required()
def create_quote():
    """Cria nova cotação"""
    data = request.json
    
    # Validações
    required_fields = ['clientId', 'clientName', 'title', 'value', 'representative', 'validUntil']
    for field in required_fields:
        if not data.get(field):
            return jsonify({'error': f'Campo {field} é obrigatório'}), 400
    
    try:
        valid_until = datetime.fromisoformat(data['validUntil'].replace('Z', '+00:00'))
    except ValueError:
        return jsonify({'error': 'Formato de data inválido para validUntil'}), 400
    
    quote = Quote(
        client_id=data['clientId'],
        client_name=data['clientName'],
        title=data['title'],
        description=data.get('description', ''),
        value=float(data['value']),
        representative=data['representative'],
        valid_until=valid_until,
        status=data.get('status', 'Pendente')
    )
    
    db.session.add(quote)
    db.session.commit()
    
    return jsonify(quote.to_dict()), 201

@quotes_bp.route('/quotes/<int:quote_id>', methods=['GET'])
@jwt_required()
def get_quote(quote_id):
    """Retorna cotação específica"""
    quote = Quote.query.get_or_404(quote_id)
    return jsonify(quote.to_dict())

@quotes_bp.route('/quotes/<int:quote_id>', methods=['PUT'])
@jwt_required()
def update_quote(quote_id):
    """Atualiza cotação"""
    quote = Quote.query.get_or_404(quote_id)
    data = request.json
    
    # Atualizar campos
    if 'clientId' in data:
        quote.client_id = data['clientId']
    if 'clientName' in data:
        quote.client_name = data['clientName']
    if 'title' in data:
        quote.title = data['title']
    if 'description' in data:
        quote.description = data['description']
    if 'value' in data:
        quote.value = float(data['value'])
    if 'representative' in data:
        quote.representative = data['representative']
    if 'status' in data:
        quote.status = data['status']
    if 'validUntil' in data:
        try:
            quote.valid_until = datetime.fromisoformat(data['validUntil'].replace('Z', '+00:00'))
        except ValueError:
            return jsonify({'error': 'Formato de data inválido para validUntil'}), 400
    
    quote.updated_at = datetime.utcnow()
    db.session.commit()
    
    return jsonify(quote.to_dict())

@quotes_bp.route('/quotes/<int:quote_id>', methods=['DELETE'])
@jwt_required()
def delete_quote(quote_id):
    """Exclui cotação"""
    quote = Quote.query.get_or_404(quote_id)
    db.session.delete(quote)
    db.session.commit()
    
    return '', 204

@quotes_bp.route('/quotes/status/<status>', methods=['GET'])
@jwt_required()
def get_quotes_by_status(status):
    """Lista cotações por status"""
    quotes = Quote.query.filter_by(status=status).order_by(Quote.created_at.desc()).all()
    return jsonify([quote.to_dict() for quote in quotes])

@quotes_bp.route('/quotes/client/<int:client_id>', methods=['GET'])
@jwt_required()
def get_quotes_by_client(client_id):
    """Lista cotações de um cliente específico"""
    quotes = Quote.query.filter_by(client_id=client_id).order_by(Quote.created_at.desc()).all()
    return jsonify([quote.to_dict() for quote in quotes])

@quotes_bp.route('/quotes/stats', methods=['GET'])
@jwt_required()
def get_quotes_stats():
    """Retorna estatísticas das cotações"""
    total_quotes = Quote.query.count()
    pending_quotes = Quote.query.filter_by(status='Pendente').count()
    approved_quotes = Quote.query.filter_by(status='Aprovada').count()
    rejected_quotes = Quote.query.filter_by(status='Rejeitada').count()
    
    # Valor total das cotações aprovadas
    approved_value = db.session.query(db.func.sum(Quote.value)).filter_by(status='Aprovada').scalar() or 0
    
    # Valor total das cotações pendentes
    pending_value = db.session.query(db.func.sum(Quote.value)).filter_by(status='Pendente').scalar() or 0
    
    return jsonify({
        'totalQuotes': total_quotes,
        'pendingQuotes': pending_quotes,
        'approvedQuotes': approved_quotes,
        'rejectedQuotes': rejected_quotes,
        'approvedValue': float(approved_value),
        'pendingValue': float(pending_value),
        'conversionRate': (approved_quotes / total_quotes * 100) if total_quotes > 0 else 0
    })
