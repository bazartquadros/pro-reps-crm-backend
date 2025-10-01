from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.models.user import User, db
from src.models.company import Company
from datetime import datetime

companies_bp = Blueprint('companies', __name__)

@companies_bp.route('/companies', methods=['GET'])
@jwt_required()
def get_companies():
    """Lista todas as empresas representadas"""
    companies = Company.query.order_by(Company.name).all()
    return jsonify([company.to_dict() for company in companies])

@companies_bp.route('/companies', methods=['POST'])
@jwt_required()
def create_company():
    """Cria nova empresa representada"""
    data = request.json
    
    # Validações
    if not data.get('name'):
        return jsonify({'error': 'Nome da empresa é obrigatório'}), 400
    
    company = Company(
        name=data['name'],
        cnpj=data.get('cnpj', ''),
        email=data.get('email', ''),
        phone=data.get('phone', ''),
        website=data.get('website', ''),
        address=data.get('address', ''),
        city=data.get('city', ''),
        state=data.get('state', ''),
        zip_code=data.get('zipCode', ''),
        segment=data.get('segment', ''),
        contact_person=data.get('contactPerson', ''),
        contact_email=data.get('contactEmail', ''),
        contact_phone=data.get('contactPhone', ''),
        commission_rate=float(data.get('commissionRate', 0.0)),
        status=data.get('status', 'Ativa'),
        notes=data.get('notes', '')
    )
    
    # Processar datas de contrato se fornecidas
    if data.get('contractStart'):
        try:
            company.contract_start = datetime.fromisoformat(data['contractStart'].replace('Z', '+00:00'))
        except ValueError:
            return jsonify({'error': 'Formato de data inválido para contractStart'}), 400
    
    if data.get('contractEnd'):
        try:
            company.contract_end = datetime.fromisoformat(data['contractEnd'].replace('Z', '+00:00'))
        except ValueError:
            return jsonify({'error': 'Formato de data inválido para contractEnd'}), 400
    
    db.session.add(company)
    db.session.commit()
    
    return jsonify(company.to_dict()), 201

@companies_bp.route('/companies/<int:company_id>', methods=['GET'])
@jwt_required()
def get_company(company_id):
    """Retorna empresa específica"""
    company = Company.query.get_or_404(company_id)
    return jsonify(company.to_dict())

@companies_bp.route('/companies/<int:company_id>', methods=['PUT'])
@jwt_required()
def update_company(company_id):
    """Atualiza empresa"""
    company = Company.query.get_or_404(company_id)
    data = request.json
    
    # Atualizar campos
    if 'name' in data:
        company.name = data['name']
    if 'cnpj' in data:
        company.cnpj = data['cnpj']
    if 'email' in data:
        company.email = data['email']
    if 'phone' in data:
        company.phone = data['phone']
    if 'website' in data:
        company.website = data['website']
    if 'address' in data:
        company.address = data['address']
    if 'city' in data:
        company.city = data['city']
    if 'state' in data:
        company.state = data['state']
    if 'zipCode' in data:
        company.zip_code = data['zipCode']
    if 'segment' in data:
        company.segment = data['segment']
    if 'contactPerson' in data:
        company.contact_person = data['contactPerson']
    if 'contactEmail' in data:
        company.contact_email = data['contactEmail']
    if 'contactPhone' in data:
        company.contact_phone = data['contactPhone']
    if 'commissionRate' in data:
        company.commission_rate = float(data['commissionRate'])
    if 'status' in data:
        company.status = data['status']
    if 'notes' in data:
        company.notes = data['notes']
    
    # Atualizar datas de contrato
    if 'contractStart' in data:
        if data['contractStart']:
            try:
                company.contract_start = datetime.fromisoformat(data['contractStart'].replace('Z', '+00:00'))
            except ValueError:
                return jsonify({'error': 'Formato de data inválido para contractStart'}), 400
        else:
            company.contract_start = None
    
    if 'contractEnd' in data:
        if data['contractEnd']:
            try:
                company.contract_end = datetime.fromisoformat(data['contractEnd'].replace('Z', '+00:00'))
            except ValueError:
                return jsonify({'error': 'Formato de data inválido para contractEnd'}), 400
        else:
            company.contract_end = None
    
    company.updated_at = datetime.utcnow()
    db.session.commit()
    
    return jsonify(company.to_dict())

@companies_bp.route('/companies/<int:company_id>', methods=['DELETE'])
@jwt_required()
def delete_company(company_id):
    """Exclui empresa"""
    company = Company.query.get_or_404(company_id)
    db.session.delete(company)
    db.session.commit()
    
    return '', 204

@companies_bp.route('/companies/active', methods=['GET'])
@jwt_required()
def get_active_companies():
    """Lista empresas ativas"""
    companies = Company.query.filter_by(status='Ativa').order_by(Company.name).all()
    return jsonify([company.to_dict() for company in companies])

@companies_bp.route('/companies/segment/<segment>', methods=['GET'])
@jwt_required()
def get_companies_by_segment(segment):
    """Lista empresas por segmento"""
    companies = Company.query.filter_by(segment=segment).order_by(Company.name).all()
    return jsonify([company.to_dict() for company in companies])

@companies_bp.route('/companies/expiring-contracts', methods=['GET'])
@jwt_required()
def get_expiring_contracts():
    """Lista empresas com contratos vencendo nos próximos 30 dias"""
    from datetime import timedelta
    
    thirty_days_from_now = datetime.now() + timedelta(days=30)
    
    companies = Company.query.filter(
        Company.contract_end <= thirty_days_from_now,
        Company.contract_end >= datetime.now(),
        Company.status == 'Ativa'
    ).order_by(Company.contract_end).all()
    
    return jsonify([company.to_dict() for company in companies])

@companies_bp.route('/companies/stats', methods=['GET'])
@jwt_required()
def get_companies_stats():
    """Retorna estatísticas das empresas"""
    total_companies = Company.query.count()
    active_companies = Company.query.filter_by(status='Ativa').count()
    inactive_companies = Company.query.filter_by(status='Inativa').count()
    suspended_companies = Company.query.filter_by(status='Suspensa').count()
    
    # Média da taxa de comissão
    avg_commission = db.session.query(db.func.avg(Company.commission_rate)).filter_by(status='Ativa').scalar() or 0
    
    # Empresas por segmento
    segments = db.session.query(
        Company.segment, 
        db.func.count(Company.id)
    ).filter_by(status='Ativa').group_by(Company.segment).all()
    
    segments_dict = {segment: count for segment, count in segments if segment}
    
    # Contratos vencendo nos próximos 30 dias
    from datetime import timedelta
    thirty_days_from_now = datetime.now() + timedelta(days=30)
    expiring_contracts = Company.query.filter(
        Company.contract_end <= thirty_days_from_now,
        Company.contract_end >= datetime.now(),
        Company.status == 'Ativa'
    ).count()
    
    return jsonify({
        'totalCompanies': total_companies,
        'activeCompanies': active_companies,
        'inactiveCompanies': inactive_companies,
        'suspendedCompanies': suspended_companies,
        'averageCommission': float(avg_commission),
        'segmentDistribution': segments_dict,
        'expiringContracts': expiring_contracts
    })
