from flask import Blueprint, request, redirect, render_template, session
from datetime import datetime

from app.middlewares.auth_middleware import require_session
from app.controllers import categoria_controller, dashboard_controller

categoria_bp = Blueprint("categorias", __name__)


@categoria_bp.route("/categorias")
@require_session
def listar():
    uid = session["user_id"]
    mes = request.args.get("mes", datetime.now().strftime("%m"))
    ano = request.args.get("ano", datetime.now().strftime("%Y"))

    data = dashboard_controller.get_categorias_data(uid, mes, ano)
    return render_template("categorias.html", **data)


@categoria_bp.route("/categorias", methods=["POST"])
@require_session
def criar():
    uid = session["user_id"]
    mes = request.form.get("mes", datetime.now().strftime("%m"))
    ano = request.form.get("ano", datetime.now().strftime("%Y"))

    categoria_controller.create(
        uid,
        nome=request.form.get("nome", "").strip(),
        cor=request.form.get("cor", "#6c63ff"),
    )
    return redirect(f"/categorias?mes={mes.zfill(2)}&ano={ano}")


@categoria_bp.route("/categorias/<int:id>/excluir", methods=["POST"])
@require_session
def excluir(id):
    uid = session["user_id"]
    mes = request.form.get("mes", datetime.now().strftime("%m"))
    ano = request.form.get("ano", datetime.now().strftime("%Y"))
    categoria_controller.delete(uid, id)
    return redirect(f"/categorias?mes={mes.zfill(2)}&ano={ano}")
