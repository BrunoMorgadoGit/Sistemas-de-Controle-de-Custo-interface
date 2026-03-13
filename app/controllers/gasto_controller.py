from flask import session
from app.models import db
from app.models.gasto import Gasto
from app.models.categoria import Categoria


MAX_LEN = 255


def create(uid, descricao, valor, categoria_id, data, anotacao):
    """Cria gasto do usuário com sanitização de campos textuais."""

    if not descricao or valor is None:
        return
    descricao = descricao[:MAX_LEN]
    anotacao = (anotacao or "")[:MAX_LEN]

    if categoria_id:
        # Impede associação com categoria de outro usuário em cenários de payload adulterado.
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
    """Atualiza gasto existente somente quando pertencer ao usuário autenticado."""

    if not descricao or valor is None:
        return
    descricao = descricao[:MAX_LEN]
    anotacao = (anotacao or "")[:MAX_LEN]

    gasto = Gasto.query.filter_by(id=gasto_id, usuario_id=uid).first()
    if not gasto:
        return

    if categoria_id:
        # Mantém integridade de ownership da categoria durante edição.
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
    """Remove gasto do usuário e sinaliza feedback para a interface."""

    gasto = Gasto.query.filter_by(id=gasto_id, usuario_id=uid).first()
    if gasto:
        db.session.delete(gasto)
        db.session.commit()
    session["toast"] = "Gasto removido!"
