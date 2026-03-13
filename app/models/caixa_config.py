from app.models import db


class CaixaConfig(db.Model):
    """Configuração de caixa por usuário (relação 1:1)."""

    __tablename__ = "caixa_config"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    saldo_inicial = db.Column(db.Float, nullable=False, default=0)
    usuario_id = db.Column(
        db.Integer, db.ForeignKey("usuarios.id", ondelete="CASCADE"), unique=True
    )

    usuario = db.relationship("Usuario", back_populates="caixa_config")

    def __repr__(self):
        return f"<CaixaConfig usuario={self.usuario_id} saldo={self.saldo_inicial}>"
