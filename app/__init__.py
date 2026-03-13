import os
from datetime import timedelta

from flask import Flask
from flask_cors import CORS

from app.extensions import limiter, csrf
from app.models import db
from app.config.settings import (
    SECRET_KEY,
    SQLALCHEMY_DATABASE_URI,
)
from app.config.database import init_db
from app.routes import register_routes

from flask_migrate import Migrate


def create_app():
    """Inicializa a aplicação Flask, extensões e políticas de segurança padrão."""

    app = Flask(
        __name__,
        template_folder=os.path.join(os.path.dirname(__file__), "..", "templates"),
        static_folder=os.path.join(os.path.dirname(__file__), "..", "static"),
    )

    app.secret_key = SECRET_KEY
    app.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE_URI
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Endurece cookies de sessão para reduzir riscos de sequestro de sessão.
    app.config["SESSION_COOKIE_HTTPONLY"] = True
    app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
    app.config["SESSION_COOKIE_SECURE"] = os.environ.get("FLASK_ENV") == "production"
    app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(hours=2)

    # Em produção, restringe CORS por variável de ambiente; em dev mantém fallback.
    allowed_origins = os.environ.get("CORS_ORIGINS", "").split(",")
    allowed_origins = [o.strip() for o in allowed_origins if o.strip()]
    CORS(app, origins=allowed_origins or ["*"], supports_credentials=True)

    csrf.init_app(app)
    limiter.init_app(app)

    db.init_app(app)

    migrate = Migrate()
    migrate.init_app(app, db)

    # Mantido para bootstrap local; em produção, o fluxo ideal é via migrations.
    init_db(app)

    @app.after_request
    def set_security_headers(response):
        """Aplica headers defensivos para reduzir superfície de ataque no browser."""
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "SAMEORIGIN"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Cache-Control"] = (
            "no-store, no-cache, must-revalidate, max-age=0"
        )
        return response

    @app.template_filter("brl")
    def fmt_brl(value):
        """Formata valores numéricos para moeda BRL no padrão brasileiro."""
        try:
            v = float(value)
            s = f"{v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            return f"R$ {s}"
        except Exception:
            return "R$ 0,00"

    @app.template_filter("fmt_date")
    def fmt_date(value):
        """Converte data ISO (YYYY-MM-DD) para DD/MM/YYYY."""
        try:
            y, m, d = str(value).split("-")
            return f"{d}/{m}/{y}"
        except Exception:
            return value or "—"

    register_routes(app)

    return app
