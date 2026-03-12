from app.models import db


class Receita(db.Model):
    __tablename__ = 'receitas'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    descricao = db.Column(db.String, nullable=False)
    valor = db.Column(db.Float, nullable=False)
    data = db.Column(db.String, nullable=False)
    anotacao = db.Column(db.String, default='')
    criado_em = db.Column(db.String, server_default=db.func.current_timestamp())
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id', ondelete='CASCADE'))

    # Relacionamentos
    usuario = db.relationship('Usuario', back_populates='receitas')

    def to_dict(self):
        return {
            'id': self.id,
            'descricao': self.descricao,
            'valor': self.valor,
            'data': self.data,
            'anotacao': self.anotacao,
            'criado_em': self.criado_em,
            'usuario_id': self.usuario_id,
        }

    def __repr__(self):
        return f'<Receita {self.descricao} R${self.valor}>'
