from app.models import db


class Categoria(db.Model):
    """Agrupa gastos do usuário e evita nomes duplicados no mesmo escopo de conta."""

    __tablename__ = "categorias"
    __table_args__ = (
        db.UniqueConstraint("nome", "usuario_id", name="uq_categoria_nome_usuario"),
    )

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nome = db.Column(db.String, nullable=False)
    cor = db.Column(db.String, default="#6c63ff")
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id", ondelete="CASCADE"))

    usuario = db.relationship("Usuario", back_populates="categorias")
    gastos = db.relationship("Gasto", back_populates="categoria", lazy="dynamic")

    def __repr__(self):
        return f"<Categoria {self.nome}>"
