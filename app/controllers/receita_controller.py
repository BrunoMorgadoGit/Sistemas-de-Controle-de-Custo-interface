from flask import session
from app.models import db
from app.models.receita import Receita

MAX_LEN = 255


def create(uid, descricao, valor, data, anotacao):
    """Cria receita do usuário com limite de tamanho em campos livres."""

    if not descricao or valor is None:
        return
    descricao = descricao[:MAX_LEN]
    anotacao = (anotacao or "")[:MAX_LEN]

    receita = Receita(
        descricao=descricao,
        valor=float(valor),
        data=data,
        anotacao=anotacao,
        usuario_id=uid,
    )
    db.session.add(receita)
    db.session.commit()
    session["toast"] = "Receita adicionada!"


def update(uid, receita_id, descricao, valor, data, anotacao):
    """Atualiza receita existente somente quando pertencer ao usuário."""

    if not descricao or valor is None:
        return
    descricao = descricao[:MAX_LEN]
    anotacao = (anotacao or "")[:MAX_LEN]

    receita = Receita.query.filter_by(id=receita_id, usuario_id=uid).first()
    if not receita:
        return

    receita.descricao = descricao
    receita.valor = float(valor)
    receita.data = data
    receita.anotacao = anotacao
    db.session.commit()
    session["toast"] = "Receita atualizada!"


def delete(uid, receita_id):
    """Exclui receita do usuário e define mensagem de retorno para a UI."""

    receita = Receita.query.filter_by(id=receita_id, usuario_id=uid).first()
    if receita:
        db.session.delete(receita)
        db.session.commit()
    session["toast"] = "Receita removida!"
