import secrets
from datetime import datetime, timedelta
from flask import session, url_for
from app.models import db
from app.models.usuario import Usuario
from app.models.categoria import Categoria
from app.models.caixa_config import CaixaConfig
from app.config.settings import CATEGORIAS_PADRAO


def process_login(email, password):
    """Retorna (sucesso: bool, dados: dict)."""
    if not email or not password:
        return False, {"error": "Email e senha são obrigatórios"}

    user = Usuario.query.filter_by(email=email).first()
    if user and user.check_password(password):
        session["user_id"] = user.id
        session["username"] = email.split('@')[0]
        return True, {}

    return False, {"error": "Email ou senha inválidos"}


def process_register(email, password):
    """Retorna (sucesso: bool, dados: dict)."""
    if not email or not password:
        return False, {
            "reg_error": "Email e senha são obrigatórios",
            "show_register": True,
        }
    if len(password) < 6:
        return False, {
            "reg_error": "A senha deve ter ao menos 6 caracteres",
            "show_register": True,
        }

    existing = Usuario.query.filter_by(email=email).first()
    if existing:
        return False, {"reg_error": "Este email já está cadastrado", "show_register": True}

    user = Usuario(email=email)
    user.set_password(password)
    db.session.add(user)
    db.session.flush()

    for nome, cor in CATEGORIAS_PADRAO:
        db.session.add(Categoria(nome=nome, cor=cor, usuario_id=user.id))

    db.session.add(CaixaConfig(saldo_inicial=0, usuario_id=user.id))
    db.session.commit()

    return True, {"success": "Conta criada com sucesso! Faça login."}


def process_forgot_password(email):
    """Gera um token de reset e retorna a URL (em logs se SMTP não configurado)."""
    if not email:
        return False, "Email é obrigatório"

    user = Usuario.query.filter_by(email=email).first()
    if not user:
        # Retornamos sucesso para evitar enumeração de contas
        return True, "Se o email estiver cadastrado, você receberá um link."

    token = secrets.token_urlsafe(32)
    user.reset_token = token
    user.reset_token_expires = datetime.now() + timedelta(hours=1)
    db.session.commit()

    # Em um app real, enviaria email aqui.
    print(f"\n[DEBUG] Link de reset para {email}: /reset-password?token={token}\n")

    return True, "Instruções enviadas para o seu email."


def process_reset_password(token, new_password):
    """Redefine a senha se o token for vílido."""
    if not token or not new_password:
        return False, "Token e senha são obrigatórios"

    user = Usuario.query.filter(
        Usuario.reset_token == token,
        Usuario.reset_token_expires > datetime.now()
    ).first()

    if not user:
        return False, "Token inválido ou expirado"

    user.set_password(new_password)
    user.reset_token = None
    user.reset_token_expires = None
    db.session.commit()

    return True, "Senha redefinida com sucesso!"
