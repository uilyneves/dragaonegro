from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.models.user import db, User, Gira, Attendance, WorkScale
from datetime import datetime

gira_bp = Blueprint('gira', __name__)

@gira_bp.route('/', methods=['GET'])
@jwt_required()
def get_giras():
    """Listar todas as giras"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'Usuário não encontrado'}), 404
        
        # Filtros opcionais
        status = request.args.get('status')
        tipo = request.args.get('tipo')
        
        query = Gira.query
        
        if status:
            query = query.filter_by(status=status)
        if tipo:
            query = query.filter_by(tipo=tipo)
        
        giras = query.order_by(Gira.data_hora.desc()).all()
        
        return jsonify({
            'giras': [gira.to_dict() for gira in giras]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@gira_bp.route('/', methods=['POST'])
@jwt_required()
def create_gira():
    """Criar nova gira (apenas grau 6+ ou Pai/Mãe de Trono)"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user or (user.grau < 6 and not user.is_pai_mae_trono()):
            return jsonify({'error': 'Acesso negado. Apenas usuários grau 6+ podem criar giras'}), 403
        
        data = request.get_json()
        
        # Validar dados obrigatórios
        required_fields = ['titulo', 'data_hora', 'tipo']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'Campo {field} é obrigatório'}), 400
        
        # Converter data_hora
        try:
            data_hora = datetime.fromisoformat(data['data_hora'].replace('Z', '+00:00'))
        except ValueError:
            return jsonify({'error': 'Formato de data/hora inválido'}), 400
        
        # Criar nova gira
        gira = Gira(
            titulo=data['titulo'],
            descricao=data.get('descricao'),
            data_hora=data_hora,
            local=data.get('local'),
            tipo=data['tipo']
        )
        
        db.session.add(gira)
        db.session.commit()
        
        return jsonify({
            'message': 'Gira criada com sucesso',
            'gira': gira.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@gira_bp.route('/<int:gira_id>', methods=['GET'])
@jwt_required()
def get_gira(gira_id):
    """Obter detalhes de uma gira específica"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'Usuário não encontrado'}), 404
        
        gira = Gira.query.get(gira_id)
        if not gira:
            return jsonify({'error': 'Gira não encontrada'}), 404
        
        # Buscar presenças e escalas
        presencas = Attendance.query.filter_by(gira_id=gira_id).all()
        escalas = WorkScale.query.filter_by(gira_id=gira_id).all()
        
        gira_data = gira.to_dict()
        gira_data['presencas'] = [p.to_dict() for p in presencas]
        gira_data['escalas'] = [e.to_dict() for e in escalas]
        
        return jsonify({'gira': gira_data}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@gira_bp.route('/<int:gira_id>/attendance', methods=['POST'])
@jwt_required()
def register_attendance(gira_id):
    """Registrar presença em gira"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'Usuário não encontrado'}), 404
        
        gira = Gira.query.get(gira_id)
        if not gira:
            return jsonify({'error': 'Gira não encontrada'}), 404
        
        data = request.get_json()
        
        # Verificar se já existe registro de presença
        existing_attendance = Attendance.query.filter_by(
            user_id=current_user_id,
            gira_id=gira_id
        ).first()
        
        if existing_attendance:
            # Atualizar registro existente
            existing_attendance.presente = data.get('presente', True)
            existing_attendance.observacoes = data.get('observacoes')
        else:
            # Criar novo registro
            attendance = Attendance(
                user_id=current_user_id,
                gira_id=gira_id,
                presente=data.get('presente', True),
                observacoes=data.get('observacoes')
            )
            db.session.add(attendance)
        
        db.session.commit()
        
        return jsonify({'message': 'Presença registrada com sucesso'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@gira_bp.route('/<int:gira_id>/work-scale', methods=['POST'])
@jwt_required()
def create_work_scale(gira_id):
    """Criar escala de trabalho para gira (apenas grau 6+ ou Pai/Mãe de Trono)"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user or (user.grau < 6 and not user.is_pai_mae_trono()):
            return jsonify({'error': 'Acesso negado. Apenas usuários grau 6+ podem criar escalas'}), 403
        
        gira = Gira.query.get(gira_id)
        if not gira:
            return jsonify({'error': 'Gira não encontrada'}), 404
        
        data = request.get_json()
        
        if not data.get('user_id') or not data.get('funcao'):
            return jsonify({'error': 'ID do usuário e função são obrigatórios'}), 400
        
        # Verificar se o usuário existe
        target_user = User.query.get(data['user_id'])
        if not target_user:
            return jsonify({'error': 'Usuário não encontrado'}), 404
        
        # Verificar se já existe escala para este usuário nesta gira
        existing_scale = WorkScale.query.filter_by(
            gira_id=gira_id,
            user_id=data['user_id']
        ).first()
        
        if existing_scale:
            return jsonify({'error': 'Usuário já possui escala para esta gira'}), 400
        
        # Criar escala
        work_scale = WorkScale(
            gira_id=gira_id,
            user_id=data['user_id'],
            funcao=data['funcao'],
            observacoes=data.get('observacoes')
        )
        
        db.session.add(work_scale)
        db.session.commit()
        
        return jsonify({
            'message': 'Escala criada com sucesso',
            'work_scale': work_scale.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@gira_bp.route('/<int:gira_id>/status', methods=['PUT'])
@jwt_required()
def update_gira_status(gira_id):
    """Atualizar status da gira (apenas grau 6+ ou Pai/Mãe de Trono)"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user or (user.grau < 6 and not user.is_pai_mae_trono()):
            return jsonify({'error': 'Acesso negado. Apenas usuários grau 6+ podem alterar status de giras'}), 403
        
        gira = Gira.query.get(gira_id)
        if not gira:
            return jsonify({'error': 'Gira não encontrada'}), 404
        
        data = request.get_json()
        
        if not data.get('status'):
            return jsonify({'error': 'Status é obrigatório'}), 400
        
        valid_statuses = ['agendada', 'realizada', 'cancelada']
        if data['status'] not in valid_statuses:
            return jsonify({'error': f'Status deve ser um dos: {", ".join(valid_statuses)}'}), 400
        
        gira.status = data['status']
        gira.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'message': 'Status da gira atualizado com sucesso',
            'gira': gira.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@gira_bp.route('/my-attendance', methods=['GET'])
@jwt_required()
def get_my_attendance():
    """Obter histórico de presenças do usuário atual"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'Usuário não encontrado'}), 404
        
        attendances = Attendance.query.filter_by(user_id=current_user_id).all()
        
        attendance_data = []
        for attendance in attendances:
            data = attendance.to_dict()
            data['gira'] = attendance.gira.to_dict()
            attendance_data.append(data)
        
        return jsonify({'attendances': attendance_data}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

