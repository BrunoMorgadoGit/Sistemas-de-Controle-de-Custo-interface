from flask import session
from app.models import db
from app.models.usuario import Usuario
from app.models.categoria import Categoria
from app.models.caixa_config import CaixaConfig
from app.config.settings import CATEGORIAS_PADRAO


def process_login(username, password):
    """Retorna (sucesso: bool, dados: dict)."""
    if not username or not password:
        return False, {"error": "Usuário e senha são obrigatórios"}

    user = Usuario.query.filter_by(username=username).first()
    if user and user.check_password(password):
        session["user_id"] = user.id
        session["username"] = user.username
        return True, {}

    return False, {"error": "Usuário ou senha inválidos"}


def process_register(username, password):
    """Retorna (sucesso: bool, dados: dict)."""
    if not username or not password:
        return False, {
            "reg_error": "Usuário e senha são obrigatórios",
            "show_register": True,
        }
    if len(password) < 6:
        return False, {
            "reg_error": "A senha deve ter ao menos 6 caracteres",
            "show_register": True,
        }

    existing = Usuario.query.filter_by(username=username).first()
    if existing:
        return False, {"reg_error": "Nome de usuário já existe", "show_register": True}

    user = Usuario(username=username)
    user.set_password(password)
    db.session.add(user)
    db.session.flush()

    for nome, cor in CATEGORIAS_PADRAO:
        db.session.add(Categoria(nome=nome, cor=cor, usuario_id=user.id))

    db.session.add(CaixaConfig(saldo_inicial=0, usuario_id=user.id))
    db.session.commit()

    return True, {"success": "Conta criada com sucesso! Faça login."}
