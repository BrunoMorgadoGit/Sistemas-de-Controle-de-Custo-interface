from functools import wraps
from flask import session, redirect

# Verifica se o usuário está logado, caso contrário redireciona para a página de login
def require_session(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            return redirect("/login")
        return f(*args, **kwargs)

    return decorated
