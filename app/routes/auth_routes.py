from flask import Blueprint, request, render_template, redirect, session

from app.extensions import limiter
from app.middlewares.auth_middleware import require_session
from app.controllers import auth_controller

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["GET", "POST"])
@limiter.limit("10 per minute", methods=["POST"])
def login_page():
    if "user_id" in session:
        return redirect("/")

    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "").strip()
        ok, data = auth_controller.process_login(email, password)
        if ok:
            session.permanent = True
            return redirect("/")
        return render_template("login.html", **data)

    return render_template("login.html")


@auth_bp.route("/register", methods=["POST"])
@limiter.limit("5 per minute")
def register_page():
    email = request.form.get("email", "").strip()
    password = request.form.get("password", "").strip()
    ok, data = auth_controller.process_register(email, password)
    return render_template("login.html", **data)


@auth_bp.route("/logout", methods=["POST"])
@require_session
def logout_page():
    session.clear()
    return redirect("/login")
