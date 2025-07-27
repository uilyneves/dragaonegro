from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import bcrypt

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Informações básicas
    nome_civil = db.Column(db.String(100), nullable=False)
    nome_ritual = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    
    # Informações espirituais
    grau = db.Column(db.Integer, default=1, nullable=False)  # 1 a 7
    entidade_cabeca_id = db.Column(db.Integer, db.ForeignKey('entities.id'), nullable=True)
    
    # Controle de acesso
    role = db.Column(db.String(50), default='filho', nullable=False)  # filho, tesoureiro, pai_mae_trono
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    entidade_cabeca = db.relationship('Entity', backref='filhos')
    presencas = db.relationship('Attendance', backref='user', lazy='dynamic')
    provas = db.relationship('Proof', backref='user', lazy='dynamic')
    diario_entries = db.relationship('DiaryEntry', backref='user', lazy='dynamic')
    
    def set_password(self, password):
        """Define a senha do usuário com hash bcrypt"""
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    def check_password(self, password):
        """Verifica se a senha está correta"""
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))
    
    def can_access_grau(self, required_grau):
        """Verifica se o usuário pode acessar conteúdo de determinado grau"""
        return self.grau >= required_grau
    
    def is_pai_mae_trono(self):
        """Verifica se o usuário é Pai/Mãe de Trono"""
        return self.role == 'pai_mae_trono'
    
    def is_tesoureiro(self):
        """Verifica se o usuário é Tesoureiro"""
        return self.role == 'tesoureiro' or self.is_pai_mae_trono()
    
    def __repr__(self):
        return f'<User {self.nome_ritual}>'
    
    def to_dict(self, include_sensitive=False):
        data = {
            'id': self.id,
            'nome_civil': self.nome_civil,
            'nome_ritual': self.nome_ritual,
            'email': self.email,
            'grau': self.grau,
            'entidade_cabeca_id': self.entidade_cabeca_id,
            'role': self.role,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        
        if include_sensitive:
            data['entidade_cabeca'] = self.entidade_cabeca.to_dict() if self.entidade_cabeca else None
            
        return data


class Entity(db.Model):
    __tablename__ = 'entities'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    tipo = db.Column(db.String(50), nullable=False)  # Exu, Pombagira, etc.
    linha = db.Column(db.String(100), nullable=True)  # Linha espiritual
    descricao = db.Column(db.Text, nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Entity {self.nome}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'nome': self.nome,
            'tipo': self.tipo,
            'linha': self.linha,
            'descricao': self.descricao,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class Gira(db.Model):
    __tablename__ = 'giras'
    
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(200), nullable=False)
    descricao = db.Column(db.Text, nullable=True)
    data_hora = db.Column(db.DateTime, nullable=False)
    local = db.Column(db.String(200), nullable=True)
    tipo = db.Column(db.String(50), nullable=False)  # desenvolvimento, consulta, festa, etc.
    status = db.Column(db.String(50), default='agendada', nullable=False)  # agendada, realizada, cancelada
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    presencas = db.relationship('Attendance', backref='gira', lazy='dynamic')
    escalas = db.relationship('WorkScale', backref='gira', lazy='dynamic')
    
    def __repr__(self):
        return f'<Gira {self.titulo}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'titulo': self.titulo,
            'descricao': self.descricao,
            'data_hora': self.data_hora.isoformat() if self.data_hora else None,
            'local': self.local,
            'tipo': self.tipo,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class Attendance(db.Model):
    __tablename__ = 'attendance'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    gira_id = db.Column(db.Integer, db.ForeignKey('giras.id'), nullable=False)
    presente = db.Column(db.Boolean, default=False, nullable=False)
    observacoes = db.Column(db.Text, nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Attendance User:{self.user_id} Gira:{self.gira_id}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'gira_id': self.gira_id,
            'presente': self.presente,
            'observacoes': self.observacoes,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class WorkScale(db.Model):
    __tablename__ = 'work_scales'
    
    id = db.Column(db.Integer, primary_key=True)
    gira_id = db.Column(db.Integer, db.ForeignKey('giras.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    funcao = db.Column(db.String(50), nullable=False)  # Ogã, Atabaqueiro, Incorporante, Guarda, Auxiliar
    observacoes = db.Column(db.Text, nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relacionamentos
    user = db.relationship('User', backref='escalas')
    
    def __repr__(self):
        return f'<WorkScale {self.funcao} - User:{self.user_id}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'gira_id': self.gira_id,
            'user_id': self.user_id,
            'funcao': self.funcao,
            'observacoes': self.observacoes,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class Proof(db.Model):
    __tablename__ = 'proofs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    titulo = db.Column(db.String(200), nullable=False)
    descricao = db.Column(db.Text, nullable=True)
    grau_requerido = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(50), default='pendente', nullable=False)  # pendente, vencida, falhada
    data_vencimento = db.Column(db.DateTime, nullable=True)
    observacoes = db.Column(db.Text, nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Proof {self.titulo}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'titulo': self.titulo,
            'descricao': self.descricao,
            'grau_requerido': self.grau_requerido,
            'status': self.status,
            'data_vencimento': self.data_vencimento.isoformat() if self.data_vencimento else None,
            'observacoes': self.observacoes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class DiaryEntry(db.Model):
    __tablename__ = 'diary_entries'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    titulo = db.Column(db.String(200), nullable=False)
    conteudo = db.Column(db.Text, nullable=False)
    tipo = db.Column(db.String(50), nullable=False)  # visao, selamento, orientacao, geral
    is_private = db.Column(db.Boolean, default=True, nullable=False)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<DiaryEntry {self.titulo}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'titulo': self.titulo,
            'conteudo': self.conteudo,
            'tipo': self.tipo,
            'is_private': self.is_private,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

