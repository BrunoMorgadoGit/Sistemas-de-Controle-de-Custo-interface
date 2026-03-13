from flask import session
from app.models import db
from app.models.investimento import Investimento

MAX_LEN = 255


def create(uid, descricao, valor, tipo, data, anotacao):
    """Cria investimento do usuário normalizando campos opcionais."""

    if not descricao or valor is None:
        return
    descricao = descricao[:MAX_LEN]
    anotacao = (anotacao or "")[:MAX_LEN]
    tipo = (tipo or "Outro")[:100]

    invest = Investimento(
        descricao=descricao,
        valor=float(valor),
        tipo=tipo,
        data=data,
        anotacao=anotacao,
        usuario_id=uid,
    )
    db.session.add(invest)
    db.session.commit()
    session["toast"] = "Investimento adicionado!"


def update(uid, invest_id, descricao, valor, tipo, data, anotacao):
    """Atualiza investimento existente quando o registro pertence ao usuário."""

    if not descricao or valor is None:
        return
    descricao = descricao[:MAX_LEN]
    anotacao = (anotacao or "")[:MAX_LEN]
    tipo = (tipo or "Outro")[:100]

    invest = Investimento.query.filter_by(id=invest_id, usuario_id=uid).first()
    if not invest:
        return

    invest.descricao = descricao
    invest.valor = float(valor)
    invest.tipo = tipo
    invest.data = data
    invest.anotacao = anotacao
    db.session.commit()
    session["toast"] = "Investimento atualizado!"


def delete(uid, invest_id):
    """Remove investimento do usuário e gera feedback de sucesso para a interface."""

    invest = Investimento.query.filter_by(id=invest_id, usuario_id=uid).first()
    if invest:
        db.session.delete(invest)
        db.session.commit()
    session["toast"] = "Investimento removido!"
