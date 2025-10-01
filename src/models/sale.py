from src.models.user import db
from datetime import datetime

class Sale(db.Model):
    __tablename__ = 'sales'
    
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    client_name = db.Column(db.String(100), nullable=False)
    product = db.Column(db.String(200), nullable=False)
    value = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), nullable=False, default='Pendente')  # Pendente, Concluída, Cancelada
    representative = db.Column(db.String(100), nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'clientId': self.client_id,
            'clientName': self.client_name,
            'product': self.product,
            'value': self.value,
            'status': self.status,
            'representative': self.representative,
            'date': self.date.isoformat() if self.date else None
        }
    
    @staticmethod
    def create_default_sales():
        """Cria vendas padrão se não existirem"""
        if Sale.query.count() == 0:
            sales = [
                Sale(
                    client_id=1,
                    client_name='João Silva',
                    product='Sistema de Gestão',
                    value=15000.00,
                    status='Concluída',
                    representative='Carlos Mendes',
                    date=datetime(2024, 6, 15)
                ),
                Sale(
                    client_id=2,
                    client_name='Maria Santos',
                    product='Consultoria em TI',
                    value=8500.00,
                    status='Pendente',
                    representative='Ana Silva',
                    date=datetime(2024, 6, 20)
                ),
                Sale(
                    client_id=3,
                    client_name='Pedro Oliveira',
                    product='Software Personalizado',
                    value=25000.00,
                    status='Concluída',
                    representative='Carlos Mendes',
                    date=datetime(2024, 6, 25)
                ),
                Sale(
                    client_id=1,
                    client_name='João Silva',
                    product='Manutenção Anual',
                    value=5000.00,
                    status='Cancelada',
                    representative='Ana Silva',
                    date=datetime(2024, 6, 28)
                )
            ]
            
            db.session.add_all(sales)
            db.session.commit()
            return True
        return False
