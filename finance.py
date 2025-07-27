from src.models.user import db
from datetime import datetime

class FinancialTransaction(db.Model):
    __tablename__ = 'financial_transactions'
    
    id = db.Column(db.Integer, primary_key=True)
    tipo = db.Column(db.String(20), nullable=False)  # entrada, saida
    categoria = db.Column(db.String(50), nullable=False)  # consulta, doacao, curso, insumo, manutencao
    descricao = db.Column(db.String(200), nullable=False)
    valor = db.Column(db.Numeric(10, 2), nullable=False)
    
    # Informações de pagamento
    metodo_pagamento = db.Column(db.String(50), nullable=True)  # pix, cartao, dinheiro
    status = db.Column(db.String(50), default='pendente', nullable=False)  # pendente, confirmado, cancelado
    
    # Relacionamentos
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  # Quem registrou
    appointment_id = db.Column(db.Integer, db.ForeignKey('appointments.id'), nullable=True)  # Se relacionado a consulta
    
    # Timestamps
    data_transacao = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    user = db.relationship('User', backref='transacoes_financeiras')
    appointment = db.relationship('Appointment', backref='transacoes')
    
    def __repr__(self):
        return f'<FinancialTransaction {self.tipo} - R$ {self.valor}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'tipo': self.tipo,
            'categoria': self.categoria,
            'descricao': self.descricao,
            'valor': float(self.valor),
            'metodo_pagamento': self.metodo_pagamento,
            'status': self.status,
            'user_id': self.user_id,
            'appointment_id': self.appointment_id,
            'data_transacao': self.data_transacao.isoformat() if self.data_transacao else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class Budget(db.Model):
    __tablename__ = 'budgets'
    
    id = db.Column(db.Integer, primary_key=True)
    mes = db.Column(db.Integer, nullable=False)  # 1-12
    ano = db.Column(db.Integer, nullable=False)
    categoria = db.Column(db.String(50), nullable=False)
    valor_orcado = db.Column(db.Numeric(10, 2), nullable=False)
    valor_realizado = db.Column(db.Numeric(10, 2), default=0, nullable=False)
    observacoes = db.Column(db.Text, nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    @property
    def percentual_realizado(self):
        """Calcula o percentual realizado do orçamento"""
        if self.valor_orcado == 0:
            return 0
        return (float(self.valor_realizado) / float(self.valor_orcado)) * 100
    
    def __repr__(self):
        return f'<Budget {self.categoria} - {self.mes}/{self.ano}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'mes': self.mes,
            'ano': self.ano,
            'categoria': self.categoria,
            'valor_orcado': float(self.valor_orcado),
            'valor_realizado': float(self.valor_realizado),
            'percentual_realizado': self.percentual_realizado,
            'observacoes': self.observacoes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class Receipt(db.Model):
    __tablename__ = 'receipts'
    
    id = db.Column(db.Integer, primary_key=True)
    numero = db.Column(db.String(50), unique=True, nullable=False)
    transaction_id = db.Column(db.Integer, db.ForeignKey('financial_transactions.id'), nullable=False)
    cliente_nome = db.Column(db.String(100), nullable=False)
    cliente_documento = db.Column(db.String(20), nullable=True)
    descricao_servico = db.Column(db.String(200), nullable=False)
    valor = db.Column(db.Numeric(10, 2), nullable=False)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relacionamentos
    transaction = db.relationship('FinancialTransaction', backref='recibo')
    
    def __repr__(self):
        return f'<Receipt {self.numero}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'numero': self.numero,
            'transaction_id': self.transaction_id,
            'cliente_nome': self.cliente_nome,
            'cliente_documento': self.cliente_documento,
            'descricao_servico': self.descricao_servico,
            'valor': float(self.valor),
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

