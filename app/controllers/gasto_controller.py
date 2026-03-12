from flask import session
from app.models import db
from app.models.gasto import Gasto
from app.models.categoria import Categoria


def create(uid, descricao, valor, categoria_id, data, anotacao):
    if not descricao or valor is None:
        return

    if categoria_id:
        cat = Categoria.query.filter_by(id=categoria_id, usuario_id=uid).first()
        if not cat:
            categoria_id = None

    gasto = Gasto(
        descricao=descricao,
        valor=float(valor),
        categoria_id=categoria_id,
        data=data,
        anotacao=anotacao,
        usuario_id=uid,
    )
    db.session.add(gasto)
    db.session.commit()
    session["toast"] = "Gasto adicionado!"


def update(uid, gasto_id, descricao, valor, categoria_id, data, anotacao):
    if not descricao or valor is None:
        return

    gasto = Gasto.query.filter_by(id=gasto_id, usuario_id=uid).first()
    if not gasto:
        return

    if categoria_id:
        cat = Categoria.query.filter_by(id=categoria_id, usuario_id=uid).first()
        if not cat:
            categoria_id = None

    gasto.descricao = descricao
    gasto.valor = float(valor)
    gasto.categoria_id = categoria_id
    gasto.data = data
    gasto.anotacao = anotacao
    db.session.commit()
    session["toast"] = "Gasto atualizado!"


def delete(uid, gasto_id):
    gasto = Gasto.query.filter_by(id=gasto_id, usuario_id=uid).first()
    if gasto:
        db.session.delete(gasto)
        db.session.commit()
    session["toast"] = "Gasto removido!"
