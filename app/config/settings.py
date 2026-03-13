import os
import secrets
from dotenv import load_dotenv

load_dotenv()

_secret = os.environ.get("SECRET_KEY")
if not _secret:
    import warnings

    warnings.warn(
        "SECRET_KEY não definida! Usando chave aleatória (sessões serão "
        "invalidadas a cada restart). Defina SECRET_KEY no .env em produção.",
        stacklevel=1,
    )
    _secret = secrets.token_hex(32)

SECRET_KEY = _secret

SQLALCHEMY_DATABASE_URI = os.environ.get(
    "DATABASE_URL",
)

EXCHANGE_API_URL = "https://open.er-api.com/v6/latest"

MESES = [
    "",
    "Janeiro",
    "Fevereiro",
    "Março",
    "Abril",
    "Maio",
    "Junho",
    "Julho",
    "Agosto",
    "Setembro",
    "Outubro",
    "Novembro",
    "Dezembro",
]

TIPOS_INVESTIMENTO = [
    "Renda Fixa",
    "Ações",
    "Fundos Imobiliários",
    "Criptomoedas",
    "Tesouro Direto",
    "Poupança",
    "CDB",
    "LCI/LCA",
    "Outro",
]

CATEGORIAS_PADRAO = [
    ("Alimentação", "#38bdf8"),
    ("Transporte", "#22d3ee"),
    ("Moradia", "#2dd4bf"),
    ("Saúde", "#818cf8"),
    ("Educação", "#a78bfa"),
    ("Lazer", "#67e8f9"),
    ("Outros", "#94a3b8"),
]
