from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from src.models.user import db, User
from datetime import datetime

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    """Endpoint para login de usuários"""
    try:
        data = request.get_json()
        
        if not data or not data.get('email') or not data.get('password'):
            return jsonify({'error': 'Email e senha são obrigatórios'}), 400
        
        email = data.get('email')
        password = data.get('password')
        
        # Buscar usuário por email
        user = User.query.filter_by(email=email).first()
        
        if not user or not user.check_password(password):
            return jsonify({'error': 'Credenciais inválidas'}), 401
        
        if not user.is_active:
            return jsonify({'error': 'Usuário inativo'}), 401
        
        # Criar token JWT
        access_token = create_access_token(identity=user.id)
        
        return jsonify({
            'access_token': access_token,
            'user': user.to_dict(include_sensitive=True)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/register', methods=['POST'])
@jwt_required()
def register():
    """Endpoint para registro de novos usuários (apenas Pai/Mãe de Trono)"""
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        if not current_user or not current_user.is_pai_mae_trono():
            return jsonify({'error': 'Acesso negado. Apenas Pai/Mãe de Trono pode registrar novos usuários'}), 403
        
        data = request.get_json()
        
        # Validar dados obrigatórios
        required_fields = ['nome_civil', 'nome_ritual', 'email', 'password']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'Campo {field} é obrigatório'}), 400
        
        # Verificar se email já existe
        if User.query.filter_by(email=data['email']).first():
            return jsonify({'error': 'Email já cadastrado'}), 400
        
        # Verificar se nome ritual já existe
        if User.query.filter_by(nome_ritual=data['nome_ritual']).first():
            return jsonify({'error': 'Nome ritual já cadastrado'}), 400
        
        # Criar novo usuário
        new_user = User(
            nome_civil=data['nome_civil'],
            nome_ritual=data['nome_ritual'],
            email=data['email'],
            grau=data.get('grau', 1),
            entidade_cabeca_id=data.get('entidade_cabeca_id'),
            role=data.get('role', 'filho')
        )
        new_user.set_password(data['password'])
        
        db.session.add(new_user)
        db.session.commit()
        
        return jsonify({
            'message': 'Usuário criado com sucesso',
            'user': new_user.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """Endpoint para obter informações do usuário atual"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'Usuário não encontrado'}), 404
        
        return jsonify({'user': user.to_dict(include_sensitive=True)}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/change-password', methods=['POST'])
@jwt_required()
def change_password():
    """Endpoint para alterar senha do usuário"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'Usuário não encontrado'}), 404
        
        data = request.get_json()
        
        if not data.get('current_password') or not data.get('new_password'):
            return jsonify({'error': 'Senha atual e nova senha são obrigatórias'}), 400
        
        # Verificar senha atual
        if not user.check_password(data['current_password']):
            return jsonify({'error': 'Senha atual incorreta'}), 400
        
        # Alterar senha
        user.set_password(data['new_password'])
        user.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({'message': 'Senha alterada com sucesso'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/promote-user', methods=['POST'])
@jwt_required()
def promote_user():
    """Endpoint para promover usuário de grau (apenas Pai/Mãe de Trono)"""
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        if not current_user or not current_user.is_pai_mae_trono():
            return jsonify({'error': 'Acesso negado. Apenas Pai/Mãe de Trono pode promover usuários'}), 403
        
        data = request.get_json()
        
        if not data.get('user_id') or not data.get('new_grau'):
            return jsonify({'error': 'ID do usuário e novo grau são obrigatórios'}), 400
        
        user = User.query.get(data['user_id'])
        if not user:
            return jsonify({'error': 'Usuário não encontrado'}), 404
        
        new_grau = data['new_grau']
        if new_grau < 1 or new_grau > 7:
            return jsonify({'error': 'Grau deve ser entre 1 e 7'}), 400
        
        old_grau = user.grau
        user.grau = new_grau
        user.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'message': f'Usuário {user.nome_ritual} promovido do grau {old_grau} para {new_grau}',
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/deactivate-user', methods=['POST'])
@jwt_required()
def deactivate_user():
    """Endpoint para desativar usuário (apenas Pai/Mãe de Trono)"""
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        if not current_user or not current_user.is_pai_mae_trono():
            return jsonify({'error': 'Acesso negado. Apenas Pai/Mãe de Trono pode desativar usuários'}), 403
        
        data = request.get_json()
        
        if not data.get('user_id'):
            return jsonify({'error': 'ID do usuário é obrigatório'}), 400
        
        user = User.query.get(data['user_id'])
        if not user:
            return jsonify({'error': 'Usuário não encontrado'}), 404
        
        if user.id == current_user_id:
            return jsonify({'error': 'Não é possível desativar seu próprio usuário'}), 400
        
        user.is_active = False
        user.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'message': f'Usuário {user.nome_ritual} desativado com sucesso'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

