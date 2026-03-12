from flask import session
from sqlalchemy.exc import IntegrityError
from app.models import db
from app.models.categoria import Categoria


def create(uid, nome, cor):
    if not nome:
        return

    try:
        cat = Categoria(nome=nome, cor=cor, usuario_id=uid)
        db.session.add(cat)
        db.session.commit()
        session["toast"] = "Categoria criada!"
    except IntegrityError:
        db.session.rollback()
        session["toast"] = "Categoria já existe!"


def delete(uid, categoria_id):
    cat = Categoria.query.filter_by(id=categoria_id, usuario_id=uid).first()
    if cat:
        db.session.delete(cat)
        db.session.commit()
    session["toast"] = "Categoria removida!"
