import os
import sys
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from sqlalchemy import text  # <--- 1. IMPORTAR A FUNÇÃO 'text'
from src.models.user import db, User
# ... (o resto dos seus imports continua igual)
from src.routes.users import users_bp

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))

# --- CONFIGURAÇÕES ---
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'default-secret-key-for-dev')
app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'default-jwt-key-for-dev')

database_url = os.environ.get('DATABASE_URL')
if database_url:
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///local_dev.db'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# --- INICIALIZAÇÃO ---
CORS(app)
jwt = JWTManager(app)
db.init_app(app)

# --- BLUEPRINTS ---
# (Seus blueprints aqui)
app.register_blueprint(auth_bp, url_prefix='/api')
app.register_blueprint(customers_bp, url_prefix='/api')
app.register_blueprint(sales_bp, url_prefix='/api')
app.register_blueprint(leads_bp, url_prefix='/api')
app.register_blueprint(quotes_bp, url_prefix='/api')
app.register_blueprint(appointments_bp, url_prefix='/api')
app.register_blueprint(companies_bp, url_prefix='/api')
app.register_blueprint(reports_bp, url_prefix='/api')
app.register_blueprint(users_bp, url_prefix='/api')


# Endpoint de health check para verificar o status da API
@app.route('/api/health')
def health_check():
    try:
        # Tenta fazer uma consulta simples para verificar a conexão com o DB
        # 2. USAR A FUNÇÃO text() AQUI
        db.session.execute(text('SELECT 1'))
        db_status = 'connected'
    except Exception as e:
        db_status = f'error: {e}'

    return jsonify({
        'status': 'ok',
        'database_status': db_status
    })

# Rota para servir a aplicação frontend
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, 'index.html')

# Bloco para execução local
if __name__ == '__main__':
    with app.app_context():
        print("Ambiente de desenvolvimento local detectado.")
        print(f"Usando banco de dados: {app.config['SQLALCHEMY_DATABASE_URI']}")
        db.create_all()
        print("Tabelas do banco de dados criadas (se não existiam).")
    app.run(host='0.0.0.0', port=5000, debug=True)
