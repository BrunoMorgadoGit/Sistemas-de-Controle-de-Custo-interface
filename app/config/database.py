from app.models import db


def init_db(app):
    """Inicializa schema base via SQLAlchemy para ambientes locais de desenvolvimento."""

    with app.app_context():
        db.create_all()
