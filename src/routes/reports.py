from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.models.user import User, db
from src.models.report import Report
from src.models.sale import Sale
from src.models.customer import Customer
from src.models.lead import Lead
from src.models.quote import Quote
from datetime import datetime, timedelta

reports_bp = Blueprint('reports', __name__)

@reports_bp.route('/reports', methods=['GET'])
@jwt_required()
def get_reports():
    """Lista todos os relatórios"""
    reports = Report.query.order_by(Report.created_at.desc()).all()
    return jsonify([report.to_dict() for report in reports])

@reports_bp.route('/reports', methods=['POST'])
@jwt_required()
def create_report():
    """Cria novo relatório"""
    data = request.json
    
    # Validações
    required_fields = ['title', 'type', 'generatedBy', 'periodStart', 'periodEnd']
    for field in required_fields:
        if not data.get(field):
            return jsonify({'error': f'Campo {field} é obrigatório'}), 400
    
    try:
        period_start = datetime.fromisoformat(data['periodStart'].replace('Z', '+00:00'))
        period_end = datetime.fromisoformat(data['periodEnd'].replace('Z', '+00:00'))
    except ValueError:
        return jsonify({'error': 'Formato de data inválido'}), 400
    
    # Gerar dados do relatório baseado no tipo
    report_data = generate_report_data(data['type'], period_start, period_end)
    
    report = Report(
        title=data['title'],
        type=data['type'],
        description=data.get('description', ''),
        generated_by=data['generatedBy'],
        period_start=period_start,
        period_end=period_end,
        data=report_data,
        status='Gerado'
    )
    
    db.session.add(report)
    db.session.commit()
    
    return jsonify(report.to_dict()), 201

@reports_bp.route('/reports/<int:report_id>', methods=['GET'])
@jwt_required()
def get_report(report_id):
    """Retorna relatório específico"""
    report = Report.query.get_or_404(report_id)
    return jsonify(report.to_dict())

@reports_bp.route('/reports/<int:report_id>', methods=['DELETE'])
@jwt_required()
def delete_report(report_id):
    """Exclui relatório"""
    report = Report.query.get_or_404(report_id)
    db.session.delete(report)
    db.session.commit()
    
    return '', 204

@reports_bp.route('/reports/generate/<report_type>', methods=['POST'])
@jwt_required()
def generate_report(report_type):
    """Gera relatório em tempo real"""
    data = request.json
    
    try:
        period_start = datetime.fromisoformat(data['periodStart'].replace('Z', '+00:00'))
        period_end = datetime.fromisoformat(data['periodEnd'].replace('Z', '+00:00'))
    except (ValueError, KeyError):
        return jsonify({'error': 'Período inválido'}), 400
    
    report_data = generate_report_data(report_type, period_start, period_end)
    
    return jsonify({
        'type': report_type,
        'periodStart': period_start.isoformat(),
        'periodEnd': period_end.isoformat(),
        'data': report_data,
        'generatedAt': datetime.utcnow().isoformat()
    })

@reports_bp.route('/reports/dashboard', methods=['GET'])
@jwt_required()
def get_dashboard_data():
    """Retorna dados para o dashboard"""
    # Período padrão: últimos 30 dias
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    
    # Estatísticas gerais
    total_customers = Customer.query.count()
    total_sales = Sale.query.filter(
        Sale.date >= start_date,
        Sale.date <= end_date
    ).count()
    total_leads = Lead.query.count()
    
    # Faturamento do período
    revenue = db.session.query(db.func.sum(Sale.value)).filter(
        Sale.date >= start_date,
        Sale.date <= end_date,
        Sale.status == 'Concluída'
    ).scalar() or 0
    
    # Vendas por representante
    sales_by_rep = db.session.query(
        Sale.representative,
        db.func.count(Sale.id),
        db.func.sum(Sale.value)
    ).filter(
        Sale.date >= start_date,
        Sale.date <= end_date,
        Sale.status == 'Concluída'
    ).group_by(Sale.representative).all()
    
    sales_by_representative = {
        rep: {'count': count, 'value': float(value or 0)}
        for rep, count, value in sales_by_rep
    }
    
    # Leads por status
    leads_by_status = db.session.query(
        Lead.status,
        db.func.count(Lead.id)
    ).group_by(Lead.status).all()
    
    leads_status_dict = {status: count for status, count in leads_by_status}
    
    return jsonify({
        'totalCustomers': total_customers,
        'totalSales': total_sales,
        'totalLeads': total_leads,
        'revenue': float(revenue),
        'salesByRepresentative': sales_by_representative,
        'leadsByStatus': leads_status_dict,
        'period': {
            'start': start_date.isoformat(),
            'end': end_date.isoformat()
        }
    })

def generate_report_data(report_type, period_start, period_end):
    """Gera dados do relatório baseado no tipo"""
    
    if report_type == 'vendas':
        # Relatório de vendas
        sales = Sale.query.filter(
            Sale.date >= period_start,
            Sale.date <= period_end
        ).all()
        
        total_value = sum(sale.value for sale in sales if sale.status == 'Concluída')
        total_count = len([sale for sale in sales if sale.status == 'Concluída'])
        avg_ticket = total_value / total_count if total_count > 0 else 0
        
        # Vendas por representante
        sales_by_rep = {}
        for sale in sales:
            if sale.status == 'Concluída':
                if sale.representative not in sales_by_rep:
                    sales_by_rep[sale.representative] = 0
                sales_by_rep[sale.representative] += sale.value
        
        # Vendas por status
        sales_by_status = {}
        for sale in sales:
            if sale.status not in sales_by_status:
                sales_by_status[sale.status] = 0
            sales_by_status[sale.status] += 1
        
        return {
            'totalValue': total_value,
            'totalCount': total_count,
            'averageTicket': avg_ticket,
            'salesByRepresentative': sales_by_rep,
            'salesByStatus': sales_by_status
        }
    
    elif report_type == 'clientes':
        # Relatório de clientes
        customers = Customer.query.all()
        total_customers = len(customers)
        
        # Novos clientes no período
        new_customers = Customer.query.filter(
            Customer.created_at >= period_start,
            Customer.created_at <= period_end
        ).count()
        
        return {
            'totalCustomers': total_customers,
            'newCustomers': new_customers,
            'growthRate': (new_customers / total_customers * 100) if total_customers > 0 else 0
        }
    
    elif report_type == 'leads':
        # Relatório de leads
        leads = Lead.query.all()
        total_leads = len(leads)
        
        # Leads por status
        leads_by_status = {}
        for lead in leads:
            if lead.status not in leads_by_status:
                leads_by_status[lead.status] = 0
            leads_by_status[lead.status] += 1
        
        # Leads por origem
        leads_by_source = {}
        for lead in leads:
            source = getattr(lead, 'source', 'Não informado')
            if source not in leads_by_source:
                leads_by_source[source] = 0
            leads_by_source[source] += 1
        
        return {
            'totalLeads': total_leads,
            'leadsByStatus': leads_by_status,
            'leadsBySource': leads_by_source
        }
    
    elif report_type == 'financeiro':
        # Relatório financeiro
        sales = Sale.query.filter(
            Sale.date >= period_start,
            Sale.date <= period_end,
            Sale.status == 'Concluída'
        ).all()
        
        total_revenue = sum(sale.value for sale in sales)
        
        # Receita por mês
        monthly_revenue = {}
        for sale in sales:
            month_key = sale.date.strftime('%Y-%m')
            if month_key not in monthly_revenue:
                monthly_revenue[month_key] = 0
            monthly_revenue[month_key] += sale.value
        
        return {
            'totalRevenue': total_revenue,
            'monthlyRevenue': monthly_revenue,
            'averageMonthlyRevenue': total_revenue / len(monthly_revenue) if monthly_revenue else 0
        }
    
    else:
        return {'message': 'Tipo de relatório não implementado'}
