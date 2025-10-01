from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from src.models.user import User, db
from datetime import datetime, timedelta

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    """Endpoint de login"""
    data = request.json
    email = data.get('email')
    password = data.get('password')
    
    if not email or not password:
        return jsonify({'error': 'Email e senha são obrigatórios'}), 400
    
    user = User.query.filter_by(email=email).first()
    
    if not user or not user.check_password(password):
        return jsonify({'error': 'Credenciais inválidas'}), 401
    
    if user.status != 'active':
        return jsonify({'error': 'Usuário inativo'}), 401
    
    # Atualiza último login
    user.last_login = datetime.utcnow()
    db.session.commit()
    
    # Cria token JWT
    access_token = create_access_token(
        identity=str(user.id),
        expires_delta=timedelta(hours=24)
    )
    
    return jsonify({
        'access_token': access_token,
        'user': user.to_dict()
    })

@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """Retorna dados do usuário atual"""
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'error': 'Usuário não encontrado'}), 404
    
    return jsonify(user.to_dict())

@auth_bp.route('/change-password', methods=['POST'])
@jwt_required()
def change_password():
    """Altera senha do usuário atual"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'error': 'Usuário não encontrado'}), 404
    
    data = request.json
    current_password = data.get('current_password')
    new_password = data.get('new_password')
    
    if not current_password or not new_password:
        return jsonify({'error': 'Senha atual e nova senha são obrigatórias'}), 400
    
    if not user.check_password(current_password):
        return jsonify({'error': 'Senha atual incorreta'}), 400
    
    if len(new_password) < 6:
        return jsonify({'error': 'Nova senha deve ter pelo menos 6 caracteres'}), 400
    
    user.set_password(new_password)
    db.session.commit()
    
    return jsonify({'message': 'Senha alterada com sucesso'})

@auth_bp.route('/users', methods=['GET'])
@jwt_required()
def get_users():
    """Lista todos os usuários (apenas admin)"""
    user_id = get_jwt_identity()
    current_user = User.query.get(user_id)
    
    if not current_user or current_user.role != 'admin':
        return jsonify({'error': 'Acesso negado'}), 403
    
    users = User.query.all()
    return jsonify([user.to_dict() for user in users])

@auth_bp.route('/users', methods=['POST'])
@jwt_required()
def create_user():
    """Cria novo usuário (apenas admin)"""
    user_id = get_jwt_identity()
    current_user = User.query.get(user_id)
    
    if not current_user or current_user.role != 'admin':
        return jsonify({'error': 'Acesso negado'}), 403
    
    data = request.json
    
    # Validações
    if not data.get('name') or not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Nome, email e senha são obrigatórios'}), 400
    
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email já está em uso'}), 400
    
    if len(data['password']) < 6:
        return jsonify({'error': 'Senha deve ter pelo menos 6 caracteres'}), 400
    
    user = User(
        name=data['name'],
        email=data['email'],
        role=data.get('role', 'representative'),
        status=data.get('status', 'active')
    )
    user.set_password(data['password'])
    
    db.session.add(user)
    db.session.commit()
    
    return jsonify(user.to_dict()), 201

@auth_bp.route('/users/<int:user_id>', methods=['PUT'])
@jwt_required()
def update_user(user_id):
    """Atualiza usuário (apenas admin)"""
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    
    if not current_user or current_user.role != 'admin':
        return jsonify({'error': 'Acesso negado'}), 403
    
    user = User.query.get_or_404(user_id)
    data = request.json
    
    # Validação de email único
    if 'email' in data and data['email'] != user.email:
        if User.query.filter_by(email=data['email']).first():
            return jsonify({'error': 'Email já está em uso'}), 400
    
    # Atualiza campos
    user.name = data.get('name', user.name)
    user.email = data.get('email', user.email)
    user.role = data.get('role', user.role)
    user.status = data.get('status', user.status)
    
    # Atualiza senha se fornecida
    if 'password' in data and data['password']:
        if len(data['password']) < 6:
            return jsonify({'error': 'Senha deve ter pelo menos 6 caracteres'}), 400
        user.set_password(data['password'])
    
    db.session.commit()
    return jsonify(user.to_dict())

@auth_bp.route('/users/<int:user_id>', methods=['DELETE'])
@jwt_required()
def delete_user(user_id):
    """Exclui usuário (apenas admin)"""
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    
    if not current_user or current_user.role != 'admin':
        return jsonify({'error': 'Acesso negado'}), 403
    
    if user_id == current_user_id:
        return jsonify({'error': 'Não é possível excluir seu próprio usuário'}), 400
    
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    
    return '', 204

@auth_bp.route('/users/<int:user_id>/toggle-status', methods=['POST'])
@jwt_required()
def toggle_user_status(user_id):
    """Alterna status do usuário (apenas admin)"""
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    
    if not current_user or current_user.role != 'admin':
        return jsonify({'error': 'Acesso negado'}), 403
    
    user = User.query.get_or_404(user_id)
    user.status = 'inactive' if user.status == 'active' else 'active'
    db.session.commit()
    
    return jsonify(user.to_dict())
