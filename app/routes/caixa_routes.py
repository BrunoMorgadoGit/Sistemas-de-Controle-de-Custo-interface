from flask import Blueprint, request, redirect, session
from datetime import datetime

from app.middlewares.auth_middleware import require_session
from app.controllers import caixa_controller

caixa_bp = Blueprint("caixa", __name__)


@caixa_bp.route("/caixa", methods=["POST"])
@require_session
def atualizar():
    uid = session["user_id"]
    mes = request.form.get("mes", datetime.now().strftime("%m"))
    ano = request.form.get("ano", datetime.now().strftime("%Y"))
    saldo_inicial = float(request.form.get("saldo_inicial", 0) or 0)

    caixa_controller.update_saldo(uid, saldo_inicial)
    return redirect(f"/?mes={mes.zfill(2)}&ano={ano}")
