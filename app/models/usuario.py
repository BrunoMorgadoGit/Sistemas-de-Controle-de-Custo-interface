from app.models import db
from werkzeug.security import generate_password_hash, check_password_hash
import bcrypt

class Usuario(db.Model):
    __tablename__ = 'usuarios'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String, nullable=False, unique=True)
    password_hash = db.Column(db.String, nullable=False)
    reset_token = db.Column(db.String, nullable=True)
    reset_token_expires = db.Column(db.DateTime, nullable=True)

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
        """Verifica senha. Suporta hashes legados PBKDF2 e migra para Bcrypt."""
        if not self.password_hash:
            return False

        if self.password_hash.startswith("$2b$"):
            return bcrypt.checkpw(
                password.encode("utf-8"),
                self.password_hash.encode("utf-8"),
            )

        try:
            valid = check_password_hash(self.password_hash, password)
        except ValueError:
            return False

        if valid:
            self.set_password(password)
            return True

        return False

    def __repr__(self):
        return f"<Usuario {self.email}>"
