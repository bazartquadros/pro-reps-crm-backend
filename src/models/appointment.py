from src.models.user import db
from datetime import datetime

class Appointment(db.Model):
    __tablename__ = 'appointments'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    client_id = db.Column(db.Integer, db.ForeignKey('customers.id'))
    client_name = db.Column(db.String(100))
    representative = db.Column(db.String(100), nullable=False)
    appointment_date = db.Column(db.DateTime, nullable=False)
    duration = db.Column(db.Integer, default=60)  # duração em minutos
    location = db.Column(db.String(200))
    type = db.Column(db.String(50), nullable=False, default='Reunião')  # Reunião, Ligação, Visita, Apresentação
    status = db.Column(db.String(20), nullable=False, default='Agendado')  # Agendado, Concluído, Cancelado, Reagendado
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'clientId': self.client_id,
            'clientName': self.client_name,
            'representative': self.representative,
            'appointmentDate': self.appointment_date.isoformat() if self.appointment_date else None,
            'duration': self.duration,
            'location': self.location,
            'type': self.type,
            'status': self.status,
            'createdAt': self.created_at.isoformat() if self.created_at else None,
            'updatedAt': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @staticmethod
    def create_default_appointments():
        """Cria compromissos padrão se não existirem"""
        if Appointment.query.count() == 0:
            appointments = [
                Appointment(
                    title='Reunião de Apresentação - Sistema de Gestão',
                    description='Apresentação da proposta de sistema de gestão empresarial para o cliente.',
                    client_id=1,
                    client_name='João Silva',
                    representative='Carlos Mendes',
                    appointment_date=datetime(2024, 10, 15, 14, 0),
                    duration=90,
                    location='Escritório do cliente - São Paulo',
                    type='Reunião',
                    status='Agendado'
                ),
                Appointment(
                    title='Follow-up - Consultoria Digital',
                    description='Acompanhamento do projeto de transformação digital em andamento.',
                    client_id=2,
                    client_name='Maria Santos',
                    representative='Ana Silva',
                    appointment_date=datetime(2024, 10, 18, 10, 30),
                    duration=60,
                    location='Videoconferência',
                    type='Ligação',
                    status='Agendado'
                ),
                Appointment(
                    title='Visita Técnica - E-commerce',
                    description='Levantamento de requisitos técnicos para desenvolvimento da plataforma de e-commerce.',
                    client_id=3,
                    client_name='Pedro Oliveira',
                    representative='Carlos Mendes',
                    appointment_date=datetime(2024, 10, 20, 16, 0),
                    duration=120,
                    location='Sede da empresa - Belo Horizonte',
                    type='Visita',
                    status='Agendado'
                ),
                Appointment(
                    title='Apresentação de Resultados',
                    description='Apresentação dos resultados obtidos no primeiro trimestre do projeto.',
                    client_id=2,
                    client_name='Maria Santos',
                    representative='Ana Silva',
                    appointment_date=datetime(2024, 9, 30, 15, 0),
                    duration=60,
                    location='Escritório Pró Reps',
                    type='Apresentação',
                    status='Concluído'
                )
            ]
            
            db.session.add_all(appointments)
            db.session.commit()
            return True
        return False
