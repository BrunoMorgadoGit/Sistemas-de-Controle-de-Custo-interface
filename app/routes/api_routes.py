from flask import Blueprint, request, jsonify

from app.extensions import csrf
from app.middlewares.auth_middleware import require_session
from app.controllers import conversao_controller

api_bp = Blueprint("api", __name__)


@api_bp.route("/api/conversao", methods=["GET"])
@csrf.exempt
@require_session
def converter_moeda():
    valor = request.args.get("valor", 0, type=float)
    de = request.args.get("de", "BRL").upper()
    para = request.args.get("para", "USD").upper()

    ok, data, status = conversao_controller.convert(valor, de, para)
    return jsonify(data), status
