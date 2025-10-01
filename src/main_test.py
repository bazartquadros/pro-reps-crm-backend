import os
import sys
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from src.models.user import db, User
from src.models.customer import Customer
from src.models.sale import Sale
from src.models.lead import Lead
from src.models.quote import Quote
from src.models.appointment import Appointment
from src.models.company import Company
from src.models.report import Report
from src.routes.auth import auth_bp
from src.routes.customers import customers_bp
from src.routes.sales import sales_bp
from src.routes.leads import leads_bp
from src.routes.quotes import quotes_bp
from src.routes.appointments import appointments_bp
from src.routes.companies import companies_bp
from src.routes.reports import reports_bp
from src.routes.users import users_bp

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
app.config['SECRET_KEY'] = 'asdf#FGSgvasgf$5$WGT'
app.config['JWT_SECRET_KEY'] = 'jwt-secret-string-change-in-production'

# Configurar CORS
CORS(app)

# Configurar JWT
jwt = JWTManager(app)

# Registrar blueprints
app.register_blueprint(auth_bp, url_prefix='/api')
app.register_blueprint(customers_bp, url_prefix='/api')
app.register_blueprint(sales_bp, url_prefix='/api')
app.register_blueprint(leads_bp, url_prefix='/api')
app.register_blueprint(quotes_bp, url_prefix='/api')
app.register_blueprint(appointments_bp, url_prefix='/api')
app.register_blueprint(companies_bp, url_prefix='/api')
app.register_blueprint(reports_bp, url_prefix='/api')
app.register_blueprint(users_bp, url_prefix='/api')

# Configuração do banco de dados - SQLite para testes
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'database', 'app_test.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# Criar diretório do banco se não existir
os.makedirs(os.path.join(os.path.dirname(__file__), 'database'), exist_ok=True)

with app.app_context():
    db.create_all()
    
    # Criar dados padrão apenas se as tabelas estiverem vazias
    try:
        User.create_default_users()
        Customer.create_default_customers()
        Sale.create_default_sales()
        Lead.create_default_leads()
        Quote.create_default_quotes()
        Appointment.create_default_appointments()
        Company.create_default_companies()
        Report.create_default_reports()
        print("Dados padrão criados com sucesso!")
    except Exception as e:
        print(f"Erro ao criar dados padrão: {e}")
        # Em caso de erro, continuar sem criar dados padrão
        pass

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
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

# Endpoint de health check
@app.route('/api/health', methods=['GET'])
def health_check():
    """Endpoint para verificar se a API está funcionando"""
    return {
        'status': 'OK',
        'message': 'Pró Reps CRM API está funcionando',
        'version': '2.0',
        'database': 'SQLite (Test Mode)'
    }

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
