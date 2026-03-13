from app.models import db


class Investimento(db.Model):
    """Entidade de alocação financeira do usuário por tipo de investimento."""

    __tablename__ = "investimentos"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    descricao = db.Column(db.String, nullable=False)
    valor = db.Column(db.Float, nullable=False)
    tipo = db.Column(db.String, nullable=False, default="Outro")
    data = db.Column(db.String, nullable=False)
    anotacao = db.Column(db.String, default="")
    criado_em = db.Column(db.String, server_default=db.func.current_timestamp())
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id", ondelete="CASCADE"))

    usuario = db.relationship("Usuario", back_populates="investimentos")

    def to_dict(self):
        """Serializa o investimento para consumo em templates e formulários."""

        return {
            "id": self.id,
            "descricao": self.descricao,
            "valor": self.valor,
            "tipo": self.tipo,
            "data": self.data,
            "anotacao": self.anotacao,
            "criado_em": self.criado_em,
        }

    def __repr__(self):
        return f"<Investimento {self.descricao} R${self.valor}>"
