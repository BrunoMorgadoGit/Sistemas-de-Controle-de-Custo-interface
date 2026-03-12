import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.environ.get("SECRET_KEY", "dev-sqlite-test-key-change-in-prod")

SQLALCHEMY_DATABASE_URI = os.environ.get(
    "DATABASE_URL",
    "postgresql://usuario:senha@localhost:5432/gestao_financeira"
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
