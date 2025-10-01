from src.models.user import db
from datetime import datetime

class Lead(db.Model):
    __tablename__ = 'leads'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    status = db.Column(db.String(20), nullable=False, default='Novo')  # Novo, Contato, Qualificado, Perdido
    source = db.Column(db.String(50))  # Website, LinkedIn, Indicação, etc.
    assigned_to = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'status': self.status,
            'source': self.source,
            'assignedTo': self.assigned_to,
            'createdAt': self.created_at.isoformat() if self.created_at else None
        }
    
    @staticmethod
    def create_default_leads():
        """Cria leads padrão se não existirem"""
        if Lead.query.count() == 0:
            leads = [
                Lead(
                    name='Carlos Ferreira',
                    email='carlos@novaempresa.com',
                    status='Novo',
                    source='Website',
                    assigned_to='Carlos Mendes',
                    created_at=datetime(2024, 6, 1)
                ),
                Lead(
                    name='Fernanda Costa',
                    email='fernanda@startup.com',
                    status='Contato',
                    source='LinkedIn',
                    assigned_to='Ana Silva',
                    created_at=datetime(2024, 6, 5)
                ),
                Lead(
                    name='Roberto Lima',
                    email='roberto@techcorp.com',
                    status='Qualificado',
                    source='Indicação',
                    assigned_to='Carlos Mendes',
                    created_at=datetime(2024, 6, 10)
                ),
                Lead(
                    name='Lucia Martins',
                    email='lucia@oldcompany.com',
                    status='Perdido',
                    source='Google Ads',
                    assigned_to='Ana Silva',
                    created_at=datetime(2024, 5, 20)
                )
            ]
            
            db.session.add_all(leads)
            db.session.commit()
            return True
        return False
