from flask import session
from app.models import db
from app.models.investimento import Investimento

# Função para criar um novo investimento
def create(uid, descricao, valor, tipo, data, anotacao):
    if not descricao or valor is None:
        return

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

# Função para atualizar um investimento existente
def update(uid, invest_id, descricao, valor, tipo, data, anotacao):
    if not descricao or valor is None:
        return

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

# Função para deletar um investimento existente
def delete(uid, invest_id):
    invest = Investimento.query.filter_by(id=invest_id, usuario_id=uid).first()
    if invest:
        db.session.delete(invest)
        db.session.commit()
    session["toast"] = "Investimento removido!"
