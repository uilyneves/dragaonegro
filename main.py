import os
import sys
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from datetime import timedelta

# Importar todos os modelos
from src.models.user import db, User, Entity, Gira, Attendance, WorkScale, Proof, DiaryEntry
from src.models.inventory import InventoryItem, InventoryMovement, GiraConsumption
from src.models.finance import FinancialTransaction, Budget, Receipt
from src.models.library import LibraryContent, ContentAccess, ForumTopic, ForumPost
from src.models.appointment import Client, Appointment, AppointmentSlot, WhatsAppMessage

# Importar blueprints
from src.routes.user import user_bp
from src.routes.auth import auth_bp
from src.routes.gira import gira_bp
from src.routes.inventory import inventory_bp
from src.routes.finance import finance_bp
from src.routes.library import library_bp
from src.routes.appointment import appointment_bp

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))

# Configurações de segurança
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'nzila-dragao-secret-key-2024')
app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'nzila-dragao-jwt-secret-2024')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)

# Configuração do banco de dados PostgreSQL
# Para desenvolvimento local, usar SQLite se PostgreSQL não estiver disponível
database_url = os.environ.get('DATABASE_URL')
if database_url:
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
else:
    # Fallback para SQLite em desenvolvimento
    app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'database', 'app.db')}"

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicializar extensões
db.init_app(app)
jwt = JWTManager(app)
CORS(app, origins="*")  # Permitir CORS para todas as origens

# Registrar blueprints
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(user_bp, url_prefix='/api/users')
app.register_blueprint(gira_bp, url_prefix='/api/giras')
app.register_blueprint(inventory_bp, url_prefix='/api/inventory')
app.register_blueprint(finance_bp, url_prefix='/api/finance')
app.register_blueprint(library_bp, url_prefix='/api/library')
app.register_blueprint(appointment_bp, url_prefix='/api/appointments')

# Criar tabelas do banco de dados
with app.app_context():
    db.create_all()
    
    # Criar dados iniciais se não existirem
    if not Entity.query.first():
        # Criar algumas entidades padrão
        entities = [
            Entity(nome='Exu Tranca Ruas', tipo='Exu', linha='Encruzilhada'),
            Entity(nome='Pombagira Maria Padilha', tipo='Pombagira', linha='Cruzeiro'),
            Entity(nome='Exu Caveira', tipo='Exu', linha='Cemitério'),
            Entity(nome='Pombagira Cigana', tipo='Pombagira', linha='Cigana'),
            Entity(nome='Exu Marabô', tipo='Exu', linha='Lira'),
        ]
        for entity in entities:
            db.session.add(entity)
        
        # Criar usuário administrador padrão
        admin_user = User(
            nome_civil='Administrador do Sistema',
            nome_ritual='Pai/Mãe de Trono',
            email='admin@nziladragao.com',
            grau=7,
            role='pai_mae_trono'
        )
        admin_user.set_password('admin123')
        db.session.add(admin_user)
        
        db.session.commit()
        print("Dados iniciais criados com sucesso!")

@app.route('/api/health')
def health_check():
    """Endpoint para verificar se a API está funcionando"""
    return {'status': 'ok', 'message': 'Nzila Dragão API está funcionando'}

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    """Servir arquivos estáticos do frontend"""
    static_folder_path = app.static_folder
    if static_folder_path is None:
        return "Static folder not configured", 404

    if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
        return send_from_directory(static_folder_path, path)
    else:
        index_path = os.path.join(static_folder_path, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(static_folder_path, 'index.html')
        else:
            return "index.html not found", 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

