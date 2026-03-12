from flask import Blueprint, request, render_template, redirect, session

from app.controllers import auth_controller

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["GET", "POST"])
def login_page():
    if "user_id" in session:
        return redirect("/")

    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "").strip()
        ok, data = auth_controller.process_login(email, password)
        if ok:
            return redirect("/")
        return render_template("login.html", **data)

    return render_template("login.html")


@auth_bp.route("/register", methods=["POST"])
def register_page():
    email = request.form.get("email", "").strip()
    password = request.form.get("password", "").strip()
    ok, data = auth_controller.process_register(email, password)
    return render_template("login.html", **data)


@auth_bp.route("/forgot-password", methods=["POST"])
def forgot_password():
    email = request.form.get("email", "").strip()
    ok, msg = auth_controller.process_forgot_password(email)
    return render_template("login.html", forgot_msg=msg)


@auth_bp.route("/reset-password", methods=["GET", "POST"])
def reset_password():
    token = request.args.get("token")
    if request.method == "POST":
        token = request.form.get("token")
        password = request.form.get("password", "").strip()
        ok, msg = auth_controller.process_reset_password(token, password)
        if ok:
            return render_template("login.html", success=msg)
        return render_template("reset_password.html", token=token, error=msg)

    return render_template("reset_password.html", token=token)


@auth_bp.route("/logout")
def logout_page():
    session.clear()
    return redirect("/login")
