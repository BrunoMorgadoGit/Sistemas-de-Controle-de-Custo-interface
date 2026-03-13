from app.models import db


class Gasto(db.Model):
    """Entidade de saída financeira associada a um usuário e, opcionalmente, a uma categoria."""

    __tablename__ = "gastos"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    descricao = db.Column(db.String, nullable=False)
    valor = db.Column(db.Float, nullable=False)
    categoria_id = db.Column(
        db.Integer, db.ForeignKey("categorias.id", ondelete="SET NULL"), nullable=True
    )
    data = db.Column(db.String, nullable=False)
    anotacao = db.Column(db.String, default="")
    criado_em = db.Column(db.String, server_default=db.func.current_timestamp())
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id", ondelete="CASCADE"))

    usuario = db.relationship("Usuario", back_populates="gastos")
    categoria = db.relationship("Categoria", back_populates="gastos")

    @property
    def categoria_nome(self):
        return self.categoria.nome if self.categoria else None

    @property
    def categoria_cor(self):
        return self.categoria.cor if self.categoria else None

    def to_dict(self):
        """Serializa o gasto para consumo direto na camada de apresentação."""

        return {
            "id": self.id,
            "descricao": self.descricao,
            "valor": self.valor,
            "categoria_id": self.categoria_id,
            "categoria_nome": self.categoria_nome,
            "categoria_cor": self.categoria_cor,
            "data": self.data,
            "anotacao": self.anotacao,
            "criado_em": self.criado_em,
        }

    def __repr__(self):
        return f"<Gasto {self.descricao} R${self.valor}>"
