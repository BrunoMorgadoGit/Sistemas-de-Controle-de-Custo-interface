from app.routes.auth_routes import auth_bp
from app.routes.dashboard_routes import dashboard_bp
from app.routes.gasto_routes import gasto_bp
from app.routes.receita_routes import receita_bp
from app.routes.investimento_routes import investimento_bp
from app.routes.categoria_routes import categoria_bp
from app.routes.caixa_routes import caixa_bp
from app.routes.api_routes import api_bp


def register_routes(app):
    """Registra todos os blueprints HTTP da aplicação."""

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(gasto_bp)
    app.register_blueprint(receita_bp)
    app.register_blueprint(investimento_bp)
    app.register_blueprint(categoria_bp)
    app.register_blueprint(caixa_bp)
    app.register_blueprint(api_bp)
