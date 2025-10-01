from src.models.user import db
from datetime import datetime

class Company(db.Model):
    __tablename__ = 'companies'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    cnpj = db.Column(db.String(18))
    email = db.Column(db.String(120))
    phone = db.Column(db.String(20))
    website = db.Column(db.String(200))
    address = db.Column(db.String(300))
    city = db.Column(db.String(100))
    state = db.Column(db.String(2))
    zip_code = db.Column(db.String(10))
    segment = db.Column(db.String(100))  # Segmento de atuação
    contact_person = db.Column(db.String(100))  # Pessoa de contato
    contact_email = db.Column(db.String(120))
    contact_phone = db.Column(db.String(20))
    commission_rate = db.Column(db.Float, default=0.0)  # Taxa de comissão
    status = db.Column(db.String(20), nullable=False, default='Ativa')  # Ativa, Inativa, Suspensa
    contract_start = db.Column(db.DateTime)
    contract_end = db.Column(db.DateTime)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'cnpj': self.cnpj,
            'email': self.email,
            'phone': self.phone,
            'website': self.website,
            'address': self.address,
            'city': self.city,
            'state': self.state,
            'zipCode': self.zip_code,
            'segment': self.segment,
            'contactPerson': self.contact_person,
            'contactEmail': self.contact_email,
            'contactPhone': self.contact_phone,
            'commissionRate': self.commission_rate,
            'status': self.status,
            'contractStart': self.contract_start.isoformat() if self.contract_start else None,
            'contractEnd': self.contract_end.isoformat() if self.contract_end else None,
            'notes': self.notes,
            'createdAt': self.created_at.isoformat() if self.created_at else None,
            'updatedAt': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @staticmethod
    def create_default_companies():
        """Cria empresas padrão se não existirem"""
        if Company.query.count() == 0:
            companies = [
                Company(
                    name='TechSolutions Brasil Ltda',
                    cnpj='12.345.678/0001-90',
                    email='contato@techsolutions.com.br',
                    phone='(11) 3456-7890',
                    website='https://www.techsolutions.com.br',
                    address='Av. Paulista, 1000 - Conjunto 501',
                    city='São Paulo',
                    state='SP',
                    zip_code='01310-100',
                    segment='Tecnologia da Informação',
                    contact_person='Roberto Silva',
                    contact_email='roberto@techsolutions.com.br',
                    contact_phone='(11) 99876-5432',
                    commission_rate=8.5,
                    status='Ativa',
                    contract_start=datetime(2024, 1, 1),
                    contract_end=datetime(2024, 12, 31),
                    notes='Empresa especializada em soluções de TI para médias e grandes empresas.'
                ),
                Company(
                    name='Inovação Digital S.A.',
                    cnpj='98.765.432/0001-10',
                    email='comercial@inovacaodigital.com.br',
                    phone='(21) 2345-6789',
                    website='https://www.inovacaodigital.com.br',
                    address='Rua das Laranjeiras, 300 - Sala 1201',
                    city='Rio de Janeiro',
                    state='RJ',
                    zip_code='22240-070',
                    segment='Transformação Digital',
                    contact_person='Fernanda Costa',
                    contact_email='fernanda@inovacaodigital.com.br',
                    contact_phone='(21) 98765-4321',
                    commission_rate=10.0,
                    status='Ativa',
                    contract_start=datetime(2024, 3, 1),
                    contract_end=datetime(2025, 2, 28),
                    notes='Especializada em consultoria para transformação digital de empresas tradicionais.'
                ),
                Company(
                    name='Automação Industrial MG',
                    cnpj='11.222.333/0001-44',
                    email='vendas@automacaomg.com.br',
                    phone='(31) 3333-4444',
                    website='https://www.automacaomg.com.br',
                    address='Rua da Indústria, 500 - Distrito Industrial',
                    city='Belo Horizonte',
                    state='MG',
                    zip_code='31270-010',
                    segment='Automação Industrial',
                    contact_person='Carlos Mendes',
                    contact_email='carlos@automacaomg.com.br',
                    contact_phone='(31) 99999-8888',
                    commission_rate=12.0,
                    status='Ativa',
                    contract_start=datetime(2023, 6, 1),
                    contract_end=datetime(2024, 5, 31),
                    notes='Líder em soluções de automação para indústrias de médio e grande porte.'
                )
            ]
            
            db.session.add_all(companies)
            db.session.commit()
            return True
        return False
