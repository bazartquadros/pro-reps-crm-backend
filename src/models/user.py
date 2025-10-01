from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import bcrypt

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='usuario')  # admin, representante, usuario
    phone = db.Column(db.String(20))
    department = db.Column(db.String(100))
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    status = db.Column(db.String(20), nullable=False, default='active')  # active, inactive (mantido para compatibilidade)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    def set_password(self, password):
        """Hash e armazena a senha"""
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    def check_password(self, password):
        """Verifica se a senha está correta"""
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))
    
    def to_dict(self):
        """Converte o objeto para dicionário"""
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'role': self.role,
            'phone': self.phone,
            'department': self.department,
            'isActive': self.is_active,
            'status': self.status,
            'createdAt': self.created_at.isoformat() if self.created_at else None,
            'updatedAt': self.updated_at.isoformat() if self.updated_at else None,
            'lastLogin': self.last_login.isoformat() if self.last_login else None
        }
    
    @staticmethod
    def create_default_users():
        """Cria usuários padrão se não existirem"""
        if User.query.count() == 0:
            # Usuário administrador
            admin = User(
                name='Administrador',
                email='admin@proreps.com',
                role='admin',
                phone='(11) 99999-0000',
                department='Administração',
                is_active=True,
                status='active'
            )
            admin.set_password('admin123')
            
            # Representantes
            carlos = User(
                name='Carlos Mendes',
                email='carlos@proreps.com',
                role='representante',
                phone='(11) 99999-1111',
                department='Vendas',
                is_active=True,
                status='active'
            )
            carlos.set_password('admin123')
            
            ana = User(
                name='Ana Silva',
                email='ana@proreps.com',
                role='representante',
                phone='(11) 99999-2222',
                department='Vendas',
                is_active=True,
                status='active'
            )
            ana.set_password('admin123')
            
            roberto = User(
                name='Roberto Santos',
                email='roberto@proreps.com',
                role='representante',
                phone='(11) 99999-3333',
                department='Vendas',
                is_active=False,
                status='inactive'
            )
            roberto.set_password('admin123')
            
            # Usuário comum
            usuario = User(
                name='João da Silva',
                email='joao@proreps.com',
                role='usuario',
                phone='(11) 99999-4444',
                department='Suporte',
                is_active=True,
                status='active'
            )
            usuario.set_password('admin123')
            
            db.session.add_all([admin, carlos, ana, roberto, usuario])
            db.session.commit()
            
            return True
        return False
