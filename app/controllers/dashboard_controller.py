from flask import session
from sqlalchemy import func

from app.models import db
from app.models.gasto import Gasto
from app.models.receita import Receita
from app.models.investimento import Investimento
from app.models.categoria import Categoria
from app.models.caixa_config import CaixaConfig
from app.config.settings import MESES, TIPOS_INVESTIMENTO


def _nav_data(mes, ano):
    """Monta estado de navegação mensal compartilhado entre as telas."""
    mes_int = int(mes)
    ano_int = int(ano)
    prev_m = 12 if mes_int == 1 else mes_int - 1
    prev_y = ano_int - 1 if mes_int == 1 else ano_int
    next_m = 1 if mes_int == 12 else mes_int + 1
    next_y = ano_int + 1 if mes_int == 12 else ano_int
    toast = session.pop("toast", None)

    return {
        "mes": mes.zfill(2),
        "ano": ano,
        "mes_nome": MESES[mes_int],
        "prev_mes": str(prev_m).zfill(2),
        "prev_ano": prev_y,
        "next_mes": str(next_m).zfill(2),
        "next_ano": next_y,
        "username": session.get("username", "Usuário"),
        "toast": toast,
    }


def get_dashboard_data(usuario_id, mes, ano, edit_caixa):
    """Consolida visão mensal do dashboard com caixa, saldo e distribuição por categoria."""

    padr = f"{ano}-{mes.zfill(2)}-%"

    gastos = Gasto.query.filter(
        Gasto.usuario_id == usuario_id, Gasto.data.like(padr)
    ).all()
    receitas = Receita.query.filter(
        Receita.usuario_id == usuario_id, Receita.data.like(padr)
    ).all()
    investimentos = Investimento.query.filter(
        Investimento.usuario_id == usuario_id, Investimento.data.like(padr)
    ).all()

    por_categoria = (
        db.session.query(
            Categoria.id,
            Categoria.nome,
            Categoria.cor,
            func.coalesce(func.sum(Gasto.valor), 0).label("total"),
        )
        .outerjoin(
            Gasto,
            db.and_(
                Gasto.categoria_id == Categoria.id,
                Gasto.data.like(padr),
                Gasto.usuario_id == usuario_id,
            ),
        )
        .filter(Categoria.usuario_id == usuario_id)
        .group_by(Categoria.id)
        .having(func.coalesce(func.sum(Gasto.valor), 0) > 0)
        .order_by(func.coalesce(func.sum(Gasto.valor), 0).desc())
        .all()
    )

    total_gastos = sum(g.valor for g in gastos)
    total_receitas = sum(r.valor for r in receitas)
    total_investimentos = sum(i.valor for i in investimentos)

    config = CaixaConfig.query.filter_by(usuario_id=usuario_id).first()
    saldo_inicial = config.saldo_inicial if config else 0

    mes_int = int(mes)
    ano_int = int(ano)
    prev_mes = 12 if mes_int == 1 else mes_int - 1
    prev_ano = ano_int - 1 if mes_int == 1 else ano_int
    # Usa dia 31 como limite textual para incluir todo o mês anterior em comparação por string.
    limite_anterior = f"{prev_ano}-{str(prev_mes).zfill(2)}-31"

    prev_receitas_val = (
        db.session.query(func.coalesce(func.sum(Receita.valor), 0))
        .filter(Receita.data <= limite_anterior, Receita.usuario_id == usuario_id)
        .scalar()
    )
    prev_gastos_val = (
        db.session.query(func.coalesce(func.sum(Gasto.valor), 0))
        .filter(Gasto.data <= limite_anterior, Gasto.usuario_id == usuario_id)
        .scalar()
    )

    caixa = saldo_inicial + prev_receitas_val - prev_gastos_val
    total_disponivel = caixa + total_receitas - total_gastos
    saldo = total_receitas - total_gastos - total_investimentos
    media = total_gastos / len(gastos) if gastos else 0

    data = {
        "por_categoria": [
            {"id": r.id, "nome": r.nome, "cor": r.cor, "total": r.total}
            for r in por_categoria
        ],
        "total_gastos": total_gastos,
        "total_receitas": total_receitas,
        "total_investimentos": total_investimentos,
        "saldo": saldo,
        "caixa": caixa,
        "total_disponivel": total_disponivel,
        "saldo_inicial": saldo_inicial,
        "quantidade": len(gastos),
        "media": media,
        "edit_caixa": edit_caixa,
    }

    return {**data, **_nav_data(mes, ano)}


def get_gastos_data(usuario_id, mes, ano, edit_gasto_id):
    """Carrega gastos do mês e dados de apoio para edição no formulário."""

    padr = f"{ano}-{mes.zfill(2)}-%"

    gastos = (
        Gasto.query.filter(Gasto.usuario_id == usuario_id, Gasto.data.like(padr))
        .order_by(Gasto.data.desc(), Gasto.id.desc())
        .all()
    )
    categorias = (
        Categoria.query.filter_by(usuario_id=usuario_id).order_by(Categoria.nome).all()
    )

    edit_gasto = None
    if edit_gasto_id:
        row = Gasto.query.filter_by(id=edit_gasto_id, usuario_id=usuario_id).first()
        edit_gasto = row.to_dict() if row else None

    data = {
        "gastos": [g.to_dict() for g in gastos],
        "categorias": [{"id": c.id, "nome": c.nome, "cor": c.cor} for c in categorias],
        "edit_gasto": edit_gasto,
    }

    return {**data, **_nav_data(mes, ano)}


def get_receitas_data(usuario_id, mes, ano, edit_receita_id):
    """Carrega receitas do mês e item selecionado para edição, quando houver."""

    padr = f"{ano}-{mes.zfill(2)}-%"

    receitas = (
        Receita.query.filter(Receita.usuario_id == usuario_id, Receita.data.like(padr))
        .order_by(Receita.data.desc(), Receita.id.desc())
        .all()
    )

    edit_receita = None
    if edit_receita_id:
        row = Receita.query.filter_by(id=edit_receita_id, usuario_id=usuario_id).first()
        edit_receita = row.to_dict() if row else None

    data = {
        "receitas": [r.to_dict() for r in receitas],
        "edit_receita": edit_receita,
    }

    return {**data, **_nav_data(mes, ano)}


def get_investimentos_data(usuario_id, mes, ano, edit_invest_id):
    """Carrega investimentos mensais e catálogo de tipos suportados pela UI."""

    padr = f"{ano}-{mes.zfill(2)}-%"

    investimentos = (
        Investimento.query.filter(
            Investimento.usuario_id == usuario_id, Investimento.data.like(padr)
        )
        .order_by(Investimento.data.desc(), Investimento.id.desc())
        .all()
    )

    edit_invest = None
    if edit_invest_id:
        row = Investimento.query.filter_by(
            id=edit_invest_id, usuario_id=usuario_id
        ).first()
        edit_invest = row.to_dict() if row else None

    data = {
        "investimentos": [i.to_dict() for i in investimentos],
        "tipos_investimento": TIPOS_INVESTIMENTO,
        "edit_invest": edit_invest,
    }

    return {**data, **_nav_data(mes, ano)}


def get_categorias_data(usuario_id, mes, ano):
    """Retorna categorias do usuário para manutenção na tela de categorias."""

    categorias = (
        Categoria.query.filter_by(usuario_id=usuario_id).order_by(Categoria.nome).all()
    )

    data = {
        "categorias": [{"id": c.id, "nome": c.nome, "cor": c.cor} for c in categorias],
    }

    return {**data, **_nav_data(mes, ano)}


def get_ferramentas_data(mes, ano):
    """Entrega contexto de navegação para a página de ferramentas."""

    return _nav_data(mes, ano)
