from flask import Blueprint, request, redirect, render_template, session
from datetime import datetime

from app.middlewares.auth_middleware import require_session
from app.controllers import gasto_controller, dashboard_controller

gasto_bp = Blueprint("gastos", __name__)


@gasto_bp.route("/gastos")
@require_session
def listar():
    uid = session["user_id"]
    mes = request.args.get("mes", datetime.now().strftime("%m"))
    ano = request.args.get("ano", datetime.now().strftime("%Y"))
    edit_gasto_id = request.args.get("edit_gasto")

    data = dashboard_controller.get_gastos_data(uid, mes, ano, edit_gasto_id)
    return render_template("gastos.html", **data)


@gasto_bp.route("/gastos", methods=["POST"])
@require_session
def criar():
    uid = session["user_id"]
    mes = request.form.get("mes", datetime.now().strftime("%m"))
    ano = request.form.get("ano", datetime.now().strftime("%Y"))

    gasto_controller.create(
        uid,
        descricao=request.form.get("descricao", "").strip(),
        valor=request.form.get("valor"),
        categoria_id=request.form.get("categoria_id") or None,
        data=request.form.get("data", datetime.now().strftime("%Y-%m-%d")),
        anotacao=request.form.get("anotacao", "").strip(),
    )
    return redirect(f"/gastos?mes={mes.zfill(2)}&ano={ano}")


@gasto_bp.route("/gastos/<int:id>", methods=["POST"])
@require_session
def editar(id):
    uid = session["user_id"]
    mes = request.form.get("mes", datetime.now().strftime("%m"))
    ano = request.form.get("ano", datetime.now().strftime("%Y"))

    gasto_controller.update(
        uid,
        id,
        descricao=request.form.get("descricao", "").strip(),
        valor=request.form.get("valor"),
        categoria_id=request.form.get("categoria_id") or None,
        data=request.form.get("data"),
        anotacao=request.form.get("anotacao", "").strip(),
    )
    return redirect(f"/gastos?mes={mes.zfill(2)}&ano={ano}")


@gasto_bp.route("/gastos/<int:id>/excluir", methods=["POST"])
@require_session
def excluir(id):
    uid = session["user_id"]
    mes = request.form.get("mes", datetime.now().strftime("%m"))
    ano = request.form.get("ano", datetime.now().strftime("%Y"))
    gasto_controller.delete(uid, id)
    return redirect(f"/gastos?mes={mes.zfill(2)}&ano={ano}")
