from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.models.user import User, db
from src.models.appointment import Appointment
from datetime import datetime, timedelta

appointments_bp = Blueprint('appointments', __name__)

@appointments_bp.route('/appointments', methods=['GET'])
@jwt_required()
def get_appointments():
    """Lista todos os compromissos"""
    appointments = Appointment.query.order_by(Appointment.appointment_date.desc()).all()
    return jsonify([appointment.to_dict() for appointment in appointments])

@appointments_bp.route('/appointments', methods=['POST'])
@jwt_required()
def create_appointment():
    """Cria novo compromisso"""
    data = request.json
    
    # Validações
    required_fields = ['title', 'representative', 'appointmentDate']
    for field in required_fields:
        if not data.get(field):
            return jsonify({'error': f'Campo {field} é obrigatório'}), 400
    
    try:
        appointment_date = datetime.fromisoformat(data['appointmentDate'].replace('Z', '+00:00'))
    except ValueError:
        return jsonify({'error': 'Formato de data inválido para appointmentDate'}), 400
    
    appointment = Appointment(
        title=data['title'],
        description=data.get('description', ''),
        client_id=data.get('clientId'),
        client_name=data.get('clientName', ''),
        representative=data['representative'],
        appointment_date=appointment_date,
        duration=data.get('duration', 60),
        location=data.get('location', ''),
        type=data.get('type', 'Reunião'),
        status=data.get('status', 'Agendado')
    )
    
    db.session.add(appointment)
    db.session.commit()
    
    return jsonify(appointment.to_dict()), 201

@appointments_bp.route('/appointments/<int:appointment_id>', methods=['GET'])
@jwt_required()
def get_appointment(appointment_id):
    """Retorna compromisso específico"""
    appointment = Appointment.query.get_or_404(appointment_id)
    return jsonify(appointment.to_dict())

@appointments_bp.route('/appointments/<int:appointment_id>', methods=['PUT'])
@jwt_required()
def update_appointment(appointment_id):
    """Atualiza compromisso"""
    appointment = Appointment.query.get_or_404(appointment_id)
    data = request.json
    
    # Atualizar campos
    if 'title' in data:
        appointment.title = data['title']
    if 'description' in data:
        appointment.description = data['description']
    if 'clientId' in data:
        appointment.client_id = data['clientId']
    if 'clientName' in data:
        appointment.client_name = data['clientName']
    if 'representative' in data:
        appointment.representative = data['representative']
    if 'appointmentDate' in data:
        try:
            appointment.appointment_date = datetime.fromisoformat(data['appointmentDate'].replace('Z', '+00:00'))
        except ValueError:
            return jsonify({'error': 'Formato de data inválido para appointmentDate'}), 400
    if 'duration' in data:
        appointment.duration = data['duration']
    if 'location' in data:
        appointment.location = data['location']
    if 'type' in data:
        appointment.type = data['type']
    if 'status' in data:
        appointment.status = data['status']
    
    appointment.updated_at = datetime.utcnow()
    db.session.commit()
    
    return jsonify(appointment.to_dict())

@appointments_bp.route('/appointments/<int:appointment_id>', methods=['DELETE'])
@jwt_required()
def delete_appointment(appointment_id):
    """Exclui compromisso"""
    appointment = Appointment.query.get_or_404(appointment_id)
    db.session.delete(appointment)
    db.session.commit()
    
    return '', 204

@appointments_bp.route('/appointments/today', methods=['GET'])
@jwt_required()
def get_today_appointments():
    """Lista compromissos de hoje"""
    today = datetime.now().date()
    appointments = Appointment.query.filter(
        db.func.date(Appointment.appointment_date) == today
    ).order_by(Appointment.appointment_date).all()
    
    return jsonify([appointment.to_dict() for appointment in appointments])

@appointments_bp.route('/appointments/week', methods=['GET'])
@jwt_required()
def get_week_appointments():
    """Lista compromissos da semana"""
    today = datetime.now().date()
    week_start = today - timedelta(days=today.weekday())
    week_end = week_start + timedelta(days=6)
    
    appointments = Appointment.query.filter(
        db.func.date(Appointment.appointment_date) >= week_start,
        db.func.date(Appointment.appointment_date) <= week_end
    ).order_by(Appointment.appointment_date).all()
    
    return jsonify([appointment.to_dict() for appointment in appointments])

@appointments_bp.route('/appointments/upcoming', methods=['GET'])
@jwt_required()
def get_upcoming_appointments():
    """Lista próximos compromissos (próximos 7 dias)"""
    today = datetime.now()
    next_week = today + timedelta(days=7)
    
    appointments = Appointment.query.filter(
        Appointment.appointment_date >= today,
        Appointment.appointment_date <= next_week,
        Appointment.status == 'Agendado'
    ).order_by(Appointment.appointment_date).all()
    
    return jsonify([appointment.to_dict() for appointment in appointments])

@appointments_bp.route('/appointments/representative/<representative>', methods=['GET'])
@jwt_required()
def get_appointments_by_representative(representative):
    """Lista compromissos de um representante específico"""
    appointments = Appointment.query.filter_by(
        representative=representative
    ).order_by(Appointment.appointment_date.desc()).all()
    
    return jsonify([appointment.to_dict() for appointment in appointments])

@appointments_bp.route('/appointments/client/<int:client_id>', methods=['GET'])
@jwt_required()
def get_appointments_by_client(client_id):
    """Lista compromissos de um cliente específico"""
    appointments = Appointment.query.filter_by(
        client_id=client_id
    ).order_by(Appointment.appointment_date.desc()).all()
    
    return jsonify([appointment.to_dict() for appointment in appointments])

@appointments_bp.route('/appointments/stats', methods=['GET'])
@jwt_required()
def get_appointments_stats():
    """Retorna estatísticas dos compromissos"""
    total_appointments = Appointment.query.count()
    scheduled_appointments = Appointment.query.filter_by(status='Agendado').count()
    completed_appointments = Appointment.query.filter_by(status='Concluído').count()
    cancelled_appointments = Appointment.query.filter_by(status='Cancelado').count()
    
    # Compromissos de hoje
    today = datetime.now().date()
    today_appointments = Appointment.query.filter(
        db.func.date(Appointment.appointment_date) == today
    ).count()
    
    # Compromissos da semana
    week_start = today - timedelta(days=today.weekday())
    week_end = week_start + timedelta(days=6)
    week_appointments = Appointment.query.filter(
        db.func.date(Appointment.appointment_date) >= week_start,
        db.func.date(Appointment.appointment_date) <= week_end
    ).count()
    
    return jsonify({
        'totalAppointments': total_appointments,
        'scheduledAppointments': scheduled_appointments,
        'completedAppointments': completed_appointments,
        'cancelledAppointments': cancelled_appointments,
        'todayAppointments': today_appointments,
        'weekAppointments': week_appointments,
        'completionRate': (completed_appointments / total_appointments * 100) if total_appointments > 0 else 0
    })
