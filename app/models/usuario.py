from app.models import db
from werkzeug.security import generate_password_hash, check_password_hash


class Usuario(db.Model):
    __tablename__ = 'usuarios'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String, nullable=False, unique=True)
    password_hash = db.Column(db.String, nullable=False)

    # Relacionamentos
    categorias = db.relationship('Categoria', back_populates='usuario',
                                 cascade='all, delete-orphan', lazy='dynamic')
    gastos = db.relationship('Gasto', back_populates='usuario',
                             cascade='all, delete-orphan', lazy='dynamic')
    receitas = db.relationship('Receita', back_populates='usuario',
                               cascade='all, delete-orphan', lazy='dynamic')
    investimentos = db.relationship('Investimento', back_populates='usuario',
                                    cascade='all, delete-orphan', lazy='dynamic')
    caixa_config = db.relationship('CaixaConfig', back_populates='usuario',
                                   uselist=False, cascade='all, delete-orphan')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<Usuario {self.username}>'
