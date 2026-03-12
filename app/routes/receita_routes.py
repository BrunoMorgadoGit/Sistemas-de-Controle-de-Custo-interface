from flask import Blueprint, request, redirect, render_template, session
from datetime import datetime

from app.middlewares.auth_middleware import require_session
from app.controllers import receita_controller, dashboard_controller

receita_bp = Blueprint("receitas", __name__)


@receita_bp.route("/receitas")
@require_session
def listar():
    uid = session["user_id"]
    mes = request.args.get("mes", datetime.now().strftime("%m"))
    ano = request.args.get("ano", datetime.now().strftime("%Y"))
    edit_receita_id = request.args.get("edit_receita")

    data = dashboard_controller.get_receitas_data(uid, mes, ano, edit_receita_id)
    return render_template("receitas.html", **data)


@receita_bp.route("/receitas", methods=["POST"])
@require_session
def criar():
    uid = session["user_id"]
    mes = request.form.get("mes", datetime.now().strftime("%m"))
    ano = request.form.get("ano", datetime.now().strftime("%Y"))

    receita_controller.create(
        uid,
        descricao=request.form.get("descricao", "").strip(),
        valor=request.form.get("valor"),
        data=request.form.get("data", datetime.now().strftime("%Y-%m-%d")),
        anotacao=request.form.get("anotacao", "").strip(),
    )
    return redirect(f"/receitas?mes={mes.zfill(2)}&ano={ano}")


@receita_bp.route("/receitas/<int:id>", methods=["POST"])
@require_session
def editar(id):
    uid = session["user_id"]
    mes = request.form.get("mes", datetime.now().strftime("%m"))
    ano = request.form.get("ano", datetime.now().strftime("%Y"))

    receita_controller.update(
        uid,
        id,
        descricao=request.form.get("descricao", "").strip(),
        valor=request.form.get("valor"),
        data=request.form.get("data"),
        anotacao=request.form.get("anotacao", "").strip(),
    )
    return redirect(f"/receitas?mes={mes.zfill(2)}&ano={ano}")


@receita_bp.route("/receitas/<int:id>/excluir", methods=["POST"])
@require_session
def excluir(id):
    uid = session["user_id"]
    mes = request.form.get("mes", datetime.now().strftime("%m"))
    ano = request.form.get("ano", datetime.now().strftime("%Y"))
    receita_controller.delete(uid, id)
    return redirect(f"/receitas?mes={mes.zfill(2)}&ano={ano}")
