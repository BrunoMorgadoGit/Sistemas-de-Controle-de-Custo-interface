from flask import session
from app.models import db
from app.models.receita import Receita

# Função para criar uma nova receita
def create(uid, descricao, valor, data, anotacao):
    if not descricao or valor is None:
        return

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

# Função para atualizar uma receita existente
def update(uid, receita_id, descricao, valor, data, anotacao):
    if not descricao or valor is None:
        return

    receita = Receita.query.filter_by(id=receita_id, usuario_id=uid).first()
    if not receita:
        return

    receita.descricao = descricao
    receita.valor = float(valor)
    receita.data = data
    receita.anotacao = anotacao
    db.session.commit()
    session["toast"] = "Receita atualizada!"

# Função para deletar uma receita existente
def delete(uid, receita_id):
    receita = Receita.query.filter_by(id=receita_id, usuario_id=uid).first()
    if receita:
        db.session.delete(receita)
        db.session.commit()
    session["toast"] = "Receita removida!"
