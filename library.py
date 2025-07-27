from src.models.user import db
from datetime import datetime

class LibraryContent(db.Model):
    __tablename__ = 'library_contents'
    
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(200), nullable=False)
    descricao = db.Column(db.Text, nullable=True)
    tipo = db.Column(db.String(50), nullable=False)  # livro, audio, video, pdf
    categoria = db.Column(db.String(50), nullable=False)  # doutrina, ritual, historia, etc.
    grau_minimo = db.Column(db.Integer, default=1, nullable=False)  # Grau mínimo para acesso
    
    # Arquivo
    arquivo_path = db.Column(db.String(500), nullable=True)
    arquivo_nome = db.Column(db.String(200), nullable=True)
    arquivo_tamanho = db.Column(db.Integer, nullable=True)  # em bytes
    
    # Metadados
    autor = db.Column(db.String(100), nullable=True)
    ano_publicacao = db.Column(db.Integer, nullable=True)
    isbn = db.Column(db.String(20), nullable=True)
    
    # Controle
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    views_count = db.Column(db.Integer, default=0, nullable=False)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    acessos = db.relationship('ContentAccess', backref='content', lazy='dynamic')
    
    def can_be_accessed_by(self, user):
        """Verifica se o usuário pode acessar este conteúdo"""
        return user.grau >= self.grau_minimo
    
    def __repr__(self):
        return f'<LibraryContent {self.titulo}>'
    
    def to_dict(self, user=None):
        data = {
            'id': self.id,
            'titulo': self.titulo,
            'descricao': self.descricao,
            'tipo': self.tipo,
            'categoria': self.categoria,
            'grau_minimo': self.grau_minimo,
            'autor': self.autor,
            'ano_publicacao': self.ano_publicacao,
            'isbn': self.isbn,
            'is_active': self.is_active,
            'views_count': self.views_count,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        
        # Só inclui informações do arquivo se o usuário pode acessar
        if user and self.can_be_accessed_by(user):
            data.update({
                'arquivo_nome': self.arquivo_nome,
                'arquivo_tamanho': self.arquivo_tamanho,
                'can_access': True
            })
        else:
            data['can_access'] = False
            
        return data


class ContentAccess(db.Model):
    __tablename__ = 'content_accesses'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    content_id = db.Column(db.Integer, db.ForeignKey('library_contents.id'), nullable=False)
    access_time = db.Column(db.DateTime, default=datetime.utcnow)
    ip_address = db.Column(db.String(45), nullable=True)
    
    # Relacionamentos
    user = db.relationship('User', backref='acessos_biblioteca')
    
    def __repr__(self):
        return f'<ContentAccess User:{self.user_id} Content:{self.content_id}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'content_id': self.content_id,
            'access_time': self.access_time.isoformat() if self.access_time else None,
            'ip_address': self.ip_address
        }


class ForumTopic(db.Model):
    __tablename__ = 'forum_topics'
    
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(200), nullable=False)
    descricao = db.Column(db.Text, nullable=True)
    categoria = db.Column(db.String(50), nullable=False)  # duvida, estudo, discussao
    grau_minimo = db.Column(db.Integer, default=1, nullable=False)
    
    # Autor
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Status
    is_closed = db.Column(db.Boolean, default=False, nullable=False)
    is_pinned = db.Column(db.Boolean, default=False, nullable=False)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    author = db.relationship('User', backref='forum_topics')
    posts = db.relationship('ForumPost', backref='topic', lazy='dynamic')
    
    @property
    def posts_count(self):
        return self.posts.count()
    
    @property
    def last_post(self):
        return self.posts.order_by(ForumPost.created_at.desc()).first()
    
    def __repr__(self):
        return f'<ForumTopic {self.titulo}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'titulo': self.titulo,
            'descricao': self.descricao,
            'categoria': self.categoria,
            'grau_minimo': self.grau_minimo,
            'author_id': self.author_id,
            'is_closed': self.is_closed,
            'is_pinned': self.is_pinned,
            'posts_count': self.posts_count,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class ForumPost(db.Model):
    __tablename__ = 'forum_posts'
    
    id = db.Column(db.Integer, primary_key=True)
    topic_id = db.Column(db.Integer, db.ForeignKey('forum_topics.id'), nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    conteudo = db.Column(db.Text, nullable=False)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    author = db.relationship('User', backref='forum_posts')
    
    def __repr__(self):
        return f'<ForumPost Topic:{self.topic_id} Author:{self.author_id}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'topic_id': self.topic_id,
            'author_id': self.author_id,
            'conteudo': self.conteudo,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

