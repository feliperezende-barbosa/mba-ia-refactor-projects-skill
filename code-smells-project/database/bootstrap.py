from database.connection import abrir_conexao
from database.schema import SCHEMA
from database.seed import popular_se_vazio


def init_db(caminho):
    db = abrir_conexao(caminho)
    try:
        db.executescript(SCHEMA)
        popular_se_vazio(db)
    finally:
        db.close()
