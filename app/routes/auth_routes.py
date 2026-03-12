from flask import Blueprint, request, render_template, redirect, session

from app.controllers import auth_controller

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["GET", "POST"])
def login_page():
    if "user_id" in session:
        return redirect("/")

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        ok, data = auth_controller.process_login(username, password)
        if ok:
            return redirect("/")
        return render_template("login.html", **data)

    return render_template("login.html")


@auth_bp.route("/register", methods=["POST"])
def register_page():
    username = request.form.get("username", "").strip()
    password = request.form.get("password", "").strip()
    ok, data = auth_controller.process_register(username, password)
    return render_template("login.html", **data)


@auth_bp.route("/logout")
def logout_page():
    session.clear()
    return redirect("/login")
