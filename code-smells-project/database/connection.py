import sqlite3
from contextlib import contextmanager

from flask import current_app, g


def abrir_conexao(caminho):
    # isolation_level=None: transações são controladas explicitamente via transaction()
    conexao = sqlite3.connect(caminho, isolation_level=None)
    conexao.row_factory = sqlite3.Row
    return conexao


def get_db():
    if "db" not in g:
        g.db = abrir_conexao(current_app.config["DATABASE_PATH"])
    return g.db


def close_db(_erro=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


@contextmanager
def transaction():
    db = get_db()
    db.execute("BEGIN IMMEDIATE")
    try:
        yield db
    except BaseException:
        db.execute("ROLLBACK")
        raise
    else:
        db.execute("COMMIT")
