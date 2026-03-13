import os

from app import create_app

app = create_app()

if __name__ == "__main__":
    print("=" * 50)
    print("  Organizador de Custos - Servidor Iniciado")
    print("  Acesse: http://localhost:5000")
    print("=" * 50)
    app.run(debug=os.environ.get("FLASK_DEBUG", "0") == "1", port=5000)
