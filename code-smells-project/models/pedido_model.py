from config.settings import STATUS_INICIAL_PEDIDO
from database.connection import get_db, transaction
from utils.errors import ValidationError


def _montar_pedidos(rows):
    pedidos = {}
    for r in rows:
        pedido = pedidos.setdefault(r["id"], {
            "id": r["id"],
            "usuario_id": r["usuario_id"],
            "status": r["status"],
            "total": r["total"],
            "criado_em": r["criado_em"],
            "itens": [],
        })
        if r["produto_id"] is not None:
            pedido["itens"].append({
                "produto_id": r["produto_id"],
                "produto_nome": r["produto_nome"] or "Desconhecido",
                "quantidade": r["quantidade"],
                "preco_unitario": r["preco_unitario"],
            })
    return list(pedidos.values())


_SELECT_PEDIDOS = """
    SELECT p.id, p.usuario_id, p.status, p.total, p.criado_em,
           i.produto_id, i.quantidade, i.preco_unitario, pr.nome AS produto_nome
    FROM pedidos p
    LEFT JOIN itens_pedido i ON i.pedido_id = p.id
    LEFT JOIN produtos pr ON pr.id = i.produto_id
"""


def listar_todos():
    rows = get_db().execute(_SELECT_PEDIDOS + " ORDER BY p.id, i.id").fetchall()
    return _montar_pedidos(rows)


def listar_por_usuario(usuario_id):
    rows = get_db().execute(
        _SELECT_PEDIDOS + " WHERE p.usuario_id = ? ORDER BY p.id, i.id", (usuario_id,)
    ).fetchall()
    return _montar_pedidos(rows)


def criar(usuario_id, itens):
    """Cria pedido, itens e baixa de estoque em uma única transação (tudo ou nada)."""
    with transaction() as db:
        total = 0
        linhas = []
        for item in itens:
            produto = db.execute(
                "SELECT id, nome, preco, estoque FROM produtos WHERE id = ?", (item["produto_id"],)
            ).fetchone()
            if produto is None:
                raise ValidationError(f"Produto {item['produto_id']} não encontrado")
            if produto["estoque"] < item["quantidade"]:
                raise ValidationError(f"Estoque insuficiente para {produto['nome']}")
            total = total + (produto["preco"] * item["quantidade"])
            linhas.append((item["produto_id"], item["quantidade"], produto["preco"]))

        pedido_id = db.execute(
            "INSERT INTO pedidos (usuario_id, status, total) VALUES (?, ?, ?)",
            (usuario_id, STATUS_INICIAL_PEDIDO, total),
        ).lastrowid
        for produto_id, quantidade, preco in linhas:
            db.execute(
                "INSERT INTO itens_pedido (pedido_id, produto_id, quantidade, preco_unitario) VALUES (?, ?, ?, ?)",
                (pedido_id, produto_id, quantidade, preco),
            )
            db.execute("UPDATE produtos SET estoque = estoque - ? WHERE id = ?", (quantidade, produto_id))
    return {"pedido_id": pedido_id, "total": total}


def atualizar_status(pedido_id, novo_status):
    cursor = get_db().execute("UPDATE pedidos SET status = ? WHERE id = ?", (novo_status, pedido_id))
    return cursor.rowcount > 0


def resumo_vendas():
    row = get_db().execute("""
        SELECT COUNT(*) AS total_pedidos,
               COALESCE(SUM(total), 0) AS faturamento,
               COALESCE(SUM(status = 'pendente'), 0) AS pendentes,
               COALESCE(SUM(status = 'aprovado'), 0) AS aprovados,
               COALESCE(SUM(status = 'cancelado'), 0) AS cancelados
        FROM pedidos
    """).fetchone()
    return dict(row)
