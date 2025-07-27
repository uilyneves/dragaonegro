from src.models.user import db
from datetime import datetime

class InventoryItem(db.Model):
    __tablename__ = 'inventory_items'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    categoria = db.Column(db.String(50), nullable=False)  # velas, bebidas, charutos, ervas, pembas, roupas, punhais
    descricao = db.Column(db.Text, nullable=True)
    quantidade_atual = db.Column(db.Integer, default=0, nullable=False)
    quantidade_minima = db.Column(db.Integer, default=5, nullable=False)
    unidade = db.Column(db.String(20), default='unidade', nullable=False)  # unidade, litro, kg, etc.
    preco_unitario = db.Column(db.Numeric(10, 2), nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    movimentacoes = db.relationship('InventoryMovement', backref='item', lazy='dynamic')
    
    @property
    def estoque_baixo(self):
        """Verifica se o estoque está baixo"""
        return self.quantidade_atual <= self.quantidade_minima
    
    def __repr__(self):
        return f'<InventoryItem {self.nome}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'nome': self.nome,
            'categoria': self.categoria,
            'descricao': self.descricao,
            'quantidade_atual': self.quantidade_atual,
            'quantidade_minima': self.quantidade_minima,
            'unidade': self.unidade,
            'preco_unitario': float(self.preco_unitario) if self.preco_unitario else None,
            'estoque_baixo': self.estoque_baixo,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class InventoryMovement(db.Model):
    __tablename__ = 'inventory_movements'
    
    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey('inventory_items.id'), nullable=False)
    tipo = db.Column(db.String(20), nullable=False)  # entrada, saida
    quantidade = db.Column(db.Integer, nullable=False)
    motivo = db.Column(db.String(200), nullable=True)
    gira_id = db.Column(db.Integer, db.ForeignKey('giras.id'), nullable=True)  # Se relacionado a uma gira
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # Quem fez a movimentação
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relacionamentos
    user = db.relationship('User', backref='movimentacoes_estoque')
    gira = db.relationship('Gira', backref='movimentacoes_estoque')
    
    def __repr__(self):
        return f'<InventoryMovement {self.tipo} - {self.quantidade}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'item_id': self.item_id,
            'tipo': self.tipo,
            'quantidade': self.quantidade,
            'motivo': self.motivo,
            'gira_id': self.gira_id,
            'user_id': self.user_id,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class GiraConsumption(db.Model):
    __tablename__ = 'gira_consumptions'
    
    id = db.Column(db.Integer, primary_key=True)
    gira_id = db.Column(db.Integer, db.ForeignKey('giras.id'), nullable=False)
    item_id = db.Column(db.Integer, db.ForeignKey('inventory_items.id'), nullable=False)
    quantidade_consumida = db.Column(db.Integer, nullable=False)
    observacoes = db.Column(db.Text, nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relacionamentos
    gira = db.relationship('Gira', backref='consumos')
    item = db.relationship('InventoryItem', backref='consumos')
    
    def __repr__(self):
        return f'<GiraConsumption Gira:{self.gira_id} Item:{self.item_id}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'gira_id': self.gira_id,
            'item_id': self.item_id,
            'quantidade_consumida': self.quantidade_consumida,
            'observacoes': self.observacoes,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

