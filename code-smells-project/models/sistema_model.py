from database.connection import get_db

TABELAS_NA_ORDEM_DE_REMOCAO = ("itens_pedido", "pedidos", "produtos", "usuarios")


def contagens():
    db = get_db()
    return {
        tabela: db.execute(f"SELECT COUNT(*) FROM {tabela}").fetchone()[0]
        for tabela in ("produtos", "usuarios", "pedidos")
    }


def resetar():
    db = get_db()
    db.execute("BEGIN")
    try:
        for tabela in TABELAS_NA_ORDEM_DE_REMOCAO:
            db.execute(f"DELETE FROM {tabela}")
        db.execute("COMMIT")
    except BaseException:
        db.execute("ROLLBACK")
        raise
