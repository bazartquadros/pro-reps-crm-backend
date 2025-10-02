import os
from flask import Flask, jsonify, send_from_directory
from sqlalchemy import text

# Importa as instâncias das extensões
from src.extensions import db, jwt, cors

# Importa os Blueprints
from src.routes.auth import auth_bp
from src.routes.customers import customers_bp
from src.routes.sales import sales_bp
from src.routes.leads import leads_bp
from src.routes.quotes import quotes_bp
from src.routes.appointments import appointments_bp
from src.routes.companies import companies_bp
from src.routes.reports import reports_bp
from src.routes.users import users_bp

def create_app():
    """Cria e configura uma instância da aplicação Flask."""
    app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))

    # --- CONFIGURAÇÕES ---
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')
    app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'dev-jwt-key')

    database_url = os.environ.get('DATABASE_URL')
    if database_url and database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)
    
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url or 'sqlite:///local_dev.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # --- INICIALIZAÇÃO DAS EXTENSÕES ---
    db.init_app(app)
    jwt.init_app(app)
    cors.init_app(app)

    # --- REGISTO DOS BLUEPRINTS ---
    app.register_blueprint(auth_bp, url_prefix='/api')
    app.register_blueprint(customers_bp, url_prefix='/api')
    app.register_blueprint(sales_bp, url_prefix='/api')
    app.register_blueprint(leads_bp, url_prefix='/api')
    app.register_blueprint(quotes_bp, url_prefix='/api')
    app.register_blueprint(appointments_bp, url_prefix='/api')
    app.register_blueprint(companies_bp, url_prefix='/api')
    app.register_blueprint(reports_bp, url_prefix='/api')
    app.register_blueprint(users_bp, url_prefix='/api')

    # --- ROTAS GLOBAIS (Health Check e Servir Frontend) ---
    @app.route('/api/health')
    def health_check():
        try:
            db.session.execute(text('SELECT 1'))
            db_status = 'connected'
        except Exception as e:
            db_status = f'error: {e}'
        return jsonify({'status': 'ok', 'database_status': db_status})

    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def serve(path):
        if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
            return send_from_directory(app.static_folder, path)
        else:
            return send_from_directory(app.static_folder, 'index.html')

    return app

# Cria a aplicação para ser usada pelo Gunicorn
app = create_app()

# Bloco para execução local
if __name__ == '__main__':
    with app.app_context():
        print("Ambiente de desenvolvimento local.")
        print(f"Banco de dados: {app.config['SQLALCHEMY_DATABASE_URI']}")
        db.create_all()
        print("Tabelas criadas.")
    app.run(host='0.0.0.0', port=5000, debug=True)
