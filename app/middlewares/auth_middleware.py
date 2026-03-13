from functools import wraps
from flask import session, redirect


def require_session(f):
    """Garante sessão autenticada antes de executar a view."""

    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            return redirect("/login")
        return f(*args, **kwargs)

    return decorated
