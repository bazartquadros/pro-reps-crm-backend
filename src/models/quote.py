from src.models.user import db
from datetime import datetime

class Quote(db.Model):
    __tablename__ = 'quotes'
    
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    client_name = db.Column(db.String(100), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    value = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), nullable=False, default='Pendente')  # Pendente, Aprovada, Rejeitada, Expirada
    representative = db.Column(db.String(100), nullable=False)
    valid_until = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'clientId': self.client_id,
            'clientName': self.client_name,
            'title': self.title,
            'description': self.description,
            'value': self.value,
            'status': self.status,
            'representative': self.representative,
            'validUntil': self.valid_until.isoformat() if self.valid_until else None,
            'createdAt': self.created_at.isoformat() if self.created_at else None,
            'updatedAt': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @staticmethod
    def create_default_quotes():
        """Cria cotações padrão se não existirem"""
        if Quote.query.count() == 0:
            quotes = [
                Quote(
                    client_id=1,
                    client_name='João Silva',
                    title='Sistema de Gestão Empresarial',
                    description='Desenvolvimento de sistema completo de gestão empresarial com módulos de vendas, estoque e financeiro.',
                    value=25000.00,
                    status='Pendente',
                    representative='Carlos Mendes',
                    valid_until=datetime(2024, 12, 31),
                    created_at=datetime(2024, 10, 1)
                ),
                Quote(
                    client_id=2,
                    client_name='Maria Santos',
                    title='Consultoria em Transformação Digital',
                    description='Consultoria especializada para modernização dos processos empresariais e implementação de tecnologias digitais.',
                    value=15000.00,
                    status='Aprovada',
                    representative='Ana Silva',
                    valid_until=datetime(2024, 11, 15),
                    created_at=datetime(2024, 9, 15)
                ),
                Quote(
                    client_id=3,
                    client_name='Pedro Oliveira',
                    title='Desenvolvimento de E-commerce',
                    description='Criação de plataforma de e-commerce completa com integração de pagamentos e gestão de produtos.',
                    value=18000.00,
                    status='Pendente',
                    representative='Carlos Mendes',
                    valid_until=datetime(2024, 11, 30),
                    created_at=datetime(2024, 9, 20)
                )
            ]
            
            db.session.add_all(quotes)
            db.session.commit()
            return True
        return False
