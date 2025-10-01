from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash
from src.models.user import User, db
from datetime import datetime, timedelta

users_bp = Blueprint('users', __name__)

@users_bp.route('/users', methods=['GET'])
@jwt_required()
def get_users():
    """Lista todos os usuários (apenas admins)"""
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    
    if not current_user or current_user.role != 'admin':
        return jsonify({'error': 'Acesso negado. Apenas administradores podem listar usuários.'}), 403
    
    users = User.query.all()
    return jsonify([user.to_dict() for user in users])

@users_bp.route('/users', methods=['POST'])
@jwt_required()
def create_user():
    """Cria novo usuário (apenas admins)"""
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    
    if not current_user or current_user.role != 'admin':
        return jsonify({'error': 'Acesso negado. Apenas administradores podem criar usuários.'}), 403
    
    data = request.json
    
    # Validações
    required_fields = ['email', 'password', 'name']
    for field in required_fields:
        if not data.get(field):
            return jsonify({'error': f'Campo {field} é obrigatório'}), 400
    
    # Verificar se email já existe
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email já está em uso'}), 400
    
    # Validar role
    valid_roles = ['admin', 'representante', 'usuario']
    role = data.get('role', 'usuario')
    if role not in valid_roles:
        return jsonify({'error': f'Role deve ser um dos seguintes: {", ".join(valid_roles)}'}), 400
    
    user = User(
        email=data['email'],
        password_hash=generate_password_hash(data['password']),
        name=data['name'],
        role=role,
        phone=data.get('phone', ''),
        department=data.get('department', ''),
        is_active=data.get('isActive', True)
    )
    
    db.session.add(user)
    db.session.commit()
    
    return jsonify(user.to_dict()), 201

@users_bp.route('/users/<int:user_id>', methods=['GET'])
@jwt_required()
def get_user(user_id):
    """Retorna usuário específico"""
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    
    # Usuários podem ver apenas seus próprios dados, admins podem ver todos
    if current_user_id != user_id and (not current_user or current_user.role != 'admin'):
        return jsonify({'error': 'Acesso negado'}), 403
    
    user = User.query.get_or_404(user_id)
    return jsonify(user.to_dict())

@users_bp.route('/users/<int:user_id>', methods=['PUT'])
@jwt_required()
def update_user(user_id):
    """Atualiza usuário"""
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    
    # Usuários podem editar apenas seus próprios dados, admins podem editar todos
    if current_user_id != user_id and (not current_user or current_user.role != 'admin'):
        return jsonify({'error': 'Acesso negado'}), 403
    
    user = User.query.get_or_404(user_id)
    data = request.json
    
    # Atualizar campos permitidos
    if 'name' in data:
        user.name = data['name']
    if 'phone' in data:
        user.phone = data['phone']
    if 'department' in data:
        user.department = data['department']
    
    # Apenas admins podem alterar email, role e status
    if current_user and current_user.role == 'admin':
        if 'email' in data:
            # Verificar se o novo email já está em uso por outro usuário
            existing_user = User.query.filter_by(email=data['email']).first()
            if existing_user and existing_user.id != user_id:
                return jsonify({'error': 'Email já está em uso'}), 400
            user.email = data['email']
        
        if 'role' in data:
            valid_roles = ['admin', 'representante', 'usuario']
            if data['role'] in valid_roles:
                user.role = data['role']
            else:
                return jsonify({'error': f'Role deve ser um dos seguintes: {", ".join(valid_roles)}'}), 400
        
        if 'isActive' in data:
            user.is_active = data['isActive']
    
    # Atualizar senha se fornecida
    if 'password' in data and data['password']:
        user.password_hash = generate_password_hash(data['password'])
    
    user.updated_at = datetime.utcnow()
    db.session.commit()
    
    return jsonify(user.to_dict())

@users_bp.route('/users/<int:user_id>', methods=['DELETE'])
@jwt_required()
def delete_user(user_id):
    """Exclui usuário (apenas admins)"""
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    
    if not current_user or current_user.role != 'admin':
        return jsonify({'error': 'Acesso negado. Apenas administradores podem excluir usuários.'}), 403
    
    # Não permitir que admin exclua a si mesmo
    if current_user_id == user_id:
        return jsonify({'error': 'Você não pode excluir sua própria conta'}), 400
    
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    
    return '', 204

@users_bp.route('/users/profile', methods=['GET'])
@jwt_required()
def get_current_user_profile():
    """Retorna perfil do usuário atual"""
    current_user_id = get_jwt_identity()
    user = User.query.get_or_404(current_user_id)
    return jsonify(user.to_dict())

@users_bp.route('/users/profile', methods=['PUT'])
@jwt_required()
def update_current_user_profile():
    """Atualiza perfil do usuário atual"""
    current_user_id = get_jwt_identity()
    user = User.query.get_or_404(current_user_id)
    data = request.json
    
    # Campos que o usuário pode atualizar em seu próprio perfil
    if 'name' in data:
        user.name = data['name']
    if 'phone' in data:
        user.phone = data['phone']
    if 'department' in data:
        user.department = data['department']
    
    # Atualizar senha se fornecida
    if 'password' in data and data['password']:
        user.password_hash = generate_password_hash(data['password'])
    
    user.updated_at = datetime.utcnow()
    db.session.commit()
    
    return jsonify(user.to_dict())

@users_bp.route('/users/change-password', methods=['POST'])
@jwt_required()
def change_password():
    """Altera senha do usuário atual"""
    current_user_id = get_jwt_identity()
    user = User.query.get_or_404(current_user_id)
    data = request.json
    
    if not data.get('currentPassword') or not data.get('newPassword'):
        return jsonify({'error': 'Senha atual e nova senha são obrigatórias'}), 400
    
    # Verificar senha atual
    if not user.check_password(data['currentPassword']):
        return jsonify({'error': 'Senha atual incorreta'}), 400
    
    # Atualizar para nova senha
    user.password_hash = generate_password_hash(data['newPassword'])
    user.updated_at = datetime.utcnow()
    db.session.commit()
    
    return jsonify({'message': 'Senha alterada com sucesso'})

@users_bp.route('/users/stats', methods=['GET'])
@jwt_required()
def get_users_stats():
    """Retorna estatísticas dos usuários (apenas admins)"""
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    
    if not current_user or current_user.role != 'admin':
        return jsonify({'error': 'Acesso negado. Apenas administradores podem ver estatísticas.'}), 403
    
    total_users = User.query.count()
    active_users = User.query.filter_by(is_active=True).count()
    inactive_users = User.query.filter_by(is_active=False).count()
    
    # Usuários por role
    users_by_role = db.session.query(
        User.role,
        db.func.count(User.id)
    ).group_by(User.role).all()
    
    roles_dict = {role: count for role, count in users_by_role}
    
    # Usuários criados nos últimos 30 dias
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    recent_users = User.query.filter(User.created_at >= thirty_days_ago).count()
    
    return jsonify({
        'totalUsers': total_users,
        'activeUsers': active_users,
        'inactiveUsers': inactive_users,
        'usersByRole': roles_dict,
        'recentUsers': recent_users
    })
