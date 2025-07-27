from src.models.user import db
from datetime import datetime

class Client(db.Model):
    __tablename__ = 'clients'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=True)
    telefone = db.Column(db.String(20), nullable=True)
    data_nascimento = db.Column(db.Date, nullable=True)
    endereco = db.Column(db.Text, nullable=True)
    
    # Informações espirituais
    observacoes = db.Column(db.Text, nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    appointments = db.relationship('Appointment', backref='client', lazy='dynamic')
    
    def __repr__(self):
        return f'<Client {self.nome}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'nome': self.nome,
            'email': self.email,
            'telefone': self.telefone,
            'data_nascimento': self.data_nascimento.isoformat() if self.data_nascimento else None,
            'endereco': self.endereco,
            'observacoes': self.observacoes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class Appointment(db.Model):
    __tablename__ = 'appointments'
    
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'), nullable=False)
    
    # Agendamento
    data_hora = db.Column(db.DateTime, nullable=False)
    motivo = db.Column(db.Text, nullable=False)
    entidade_indicada = db.Column(db.String(100), nullable=True)
    
    # Status
    status = db.Column(db.String(50), default='agendado', nullable=False)  # agendado, confirmado, realizado, cancelado
    
    # Médium responsável
    medium_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    
    # Pagamento
    valor = db.Column(db.Numeric(10, 2), nullable=True)
    metodo_pagamento = db.Column(db.String(50), nullable=True)  # pix, cartao, dinheiro
    status_pagamento = db.Column(db.String(50), default='pendente', nullable=False)  # pendente, pago, cancelado
    
    # Relatório pós-atendimento
    relatorio = db.Column(db.Text, nullable=True)
    orientacoes = db.Column(db.Text, nullable=True)
    proxima_consulta = db.Column(db.Date, nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    medium = db.relationship('User', backref='atendimentos')
    
    def __repr__(self):
        return f'<Appointment {self.client.nome} - {self.data_hora}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'client_id': self.client_id,
            'data_hora': self.data_hora.isoformat() if self.data_hora else None,
            'motivo': self.motivo,
            'entidade_indicada': self.entidade_indicada,
            'status': self.status,
            'medium_id': self.medium_id,
            'valor': float(self.valor) if self.valor else None,
            'metodo_pagamento': self.metodo_pagamento,
            'status_pagamento': self.status_pagamento,
            'relatorio': self.relatorio,
            'orientacoes': self.orientacoes,
            'proxima_consulta': self.proxima_consulta.isoformat() if self.proxima_consulta else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class AppointmentSlot(db.Model):
    __tablename__ = 'appointment_slots'
    
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.Date, nullable=False)
    hora_inicio = db.Column(db.Time, nullable=False)
    hora_fim = db.Column(db.Time, nullable=False)
    medium_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    is_available = db.Column(db.Boolean, default=True, nullable=False)
    observacoes = db.Column(db.Text, nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relacionamentos
    medium = db.relationship('User', backref='horarios_disponiveis')
    
    def __repr__(self):
        return f'<AppointmentSlot {self.data} {self.hora_inicio}-{self.hora_fim}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'data': self.data.isoformat() if self.data else None,
            'hora_inicio': self.hora_inicio.isoformat() if self.hora_inicio else None,
            'hora_fim': self.hora_fim.isoformat() if self.hora_fim else None,
            'medium_id': self.medium_id,
            'is_available': self.is_available,
            'observacoes': self.observacoes,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class WhatsAppMessage(db.Model):
    __tablename__ = 'whatsapp_messages'
    
    id = db.Column(db.Integer, primary_key=True)
    telefone = db.Column(db.String(20), nullable=False)
    mensagem = db.Column(db.Text, nullable=False)
    tipo = db.Column(db.String(50), nullable=False)  # confirmacao, lembrete, liberacao_grau, aniversario
    status = db.Column(db.String(50), default='pendente', nullable=False)  # pendente, enviado, erro
    
    # Relacionamentos opcionais
    appointment_id = db.Column(db.Integer, db.ForeignKey('appointments.id'), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    sent_at = db.Column(db.DateTime, nullable=True)
    
    # Relacionamentos
    appointment = db.relationship('Appointment', backref='mensagens_whatsapp')
    user = db.relationship('User', backref='mensagens_whatsapp')
    
    def __repr__(self):
        return f'<WhatsAppMessage {self.telefone} - {self.tipo}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'telefone': self.telefone,
            'mensagem': self.mensagem,
            'tipo': self.tipo,
            'status': self.status,
            'appointment_id': self.appointment_id,
            'user_id': self.user_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'sent_at': self.sent_at.isoformat() if self.sent_at else None
        }

