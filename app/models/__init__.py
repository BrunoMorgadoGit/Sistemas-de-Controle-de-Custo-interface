from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from app.models.usuario import Usuario
from app.models.categoria import Categoria
from app.models.gasto import Gasto
from app.models.receita import Receita
from app.models.investimento import Investimento
from app.models.caixa_config import CaixaConfig
