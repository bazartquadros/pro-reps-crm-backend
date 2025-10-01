from src.models.user import db
from datetime import datetime

class Customer(db.Model):
    __tablename__ = 'customers'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20))
    company = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'company': self.company,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    @staticmethod
    def create_default_customers():
        """Cria clientes padrão se não existirem"""
        if Customer.query.count() == 0:
            customers = [
                Customer(
                    name='João Silva',
                    email='joao@empresa.com',
                    phone='(11) 99999-9999',
                    company='Empresa ABC'
                ),
                Customer(
                    name='Maria Santos',
                    email='maria@techsolutions.com',
                    phone='(11) 88888-8888',
                    company='Tech Solutions'
                ),
                Customer(
                    name='Pedro Oliveira',
                    email='pedro@inovacao.com',
                    phone='(11) 77777-7777',
                    company='Inovação Ltda'
                )
            ]
            
            db.session.add_all(customers)
            db.session.commit()
            return True
        return False
