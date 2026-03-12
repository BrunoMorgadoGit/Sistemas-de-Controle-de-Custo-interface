from flask import Blueprint, request, render_template, session
from datetime import datetime

from app.middlewares.auth_middleware import require_session
from app.controllers import dashboard_controller

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/")
@require_session
def index():
    usuario_id = session["user_id"]
    mes = request.args.get("mes", datetime.now().strftime("%m"))
    ano = request.args.get("ano", datetime.now().strftime("%Y"))
    edit_caixa = request.args.get("edit_caixa") == "1"

    data = dashboard_controller.get_dashboard_data(usuario_id, mes, ano, edit_caixa)
    return render_template("dashboard.html", **data)


@dashboard_bp.route("/ferramentas")
@require_session
def ferramentas():
    mes = request.args.get("mes", datetime.now().strftime("%m"))
    ano = request.args.get("ano", datetime.now().strftime("%Y"))

    data = dashboard_controller.get_ferramentas_data(mes, ano)
    return render_template("ferramentas.html", **data)
