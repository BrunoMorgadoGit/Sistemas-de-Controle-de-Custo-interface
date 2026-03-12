import os
from flask import Flask
from flask_cors import CORS

from app.models import db
from app.config.settings import (
    SECRET_KEY,
    SQLALCHEMY_DATABASE_URI,
)
from app.config.database import init_db
from app.routes import register_routes

from flask_migrate import Migrate


def create_app():
    app = Flask(
        __name__,
        template_folder=os.path.join(os.path.dirname(__file__), "..", "templates"),
        static_folder=os.path.join(os.path.dirname(__file__), "..", "static"),
    )

    app.secret_key = SECRET_KEY
    app.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE_URI
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    CORS(app)
    db.init_app(app)

    # Inicializa Flask-Migrate
    migrate = Migrate()
    migrate.init_app(app, db)

    # Cria tabelas iniciais (em dev/prototipagem)
    init_db(app)

    # Filtros Jinja2
    @app.template_filter("brl")
    def fmt_brl(value):
        try:
            v = float(value)
            s = f"{v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            return f"R$ {s}"
        except Exception:
            return "R$ 0,00"

    @app.template_filter("fmt_date")
    def fmt_date(value):
        try:
            y, m, d = str(value).split("-")
            return f"{d}/{m}/{y}"
        except Exception:
            return value or "—"

    register_routes(app)

    return app
