from flask import session
from app.models import db
from app.models.caixa_config import CaixaConfig


def update_saldo(uid, saldo_inicial):
    """Atualiza saldo inicial do caixa, criando configuração quando ausente."""

    config = CaixaConfig.query.filter_by(usuario_id=uid).first()
    if config:
        config.saldo_inicial = saldo_inicial
    else:
        config = CaixaConfig(saldo_inicial=saldo_inicial, usuario_id=uid)
        db.session.add(config)

    db.session.commit()
    session["toast"] = "Saldo inicial atualizado!"
