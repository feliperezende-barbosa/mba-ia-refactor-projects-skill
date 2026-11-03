import os
import secrets


def _flag(name, default="false"):
    return os.environ.get(name, default).lower() in ("1", "true", "yes")


class Settings:
    SECRET_KEY = os.environ.get("SECRET_KEY") or secrets.token_hex(32)
    DEBUG = _flag("FLASK_DEBUG")
    HOST = os.environ.get("HOST", "127.0.0.1")
    PORT = int(os.environ.get("PORT", "5000"))
    DATABASE_PATH = os.environ.get("DATABASE_PATH", "loja.db")
    ENVIRONMENT = os.environ.get("APP_ENV", "desenvolvimento")
    API_VERSION = "1.0.0"
    ADMIN_TOKEN = os.environ.get("ADMIN_TOKEN", "")


CATEGORIAS_VALIDAS = ("informatica", "moveis", "vestuario", "geral", "eletronicos", "livros")
CATEGORIA_PADRAO = "geral"

STATUS_PEDIDO = ("pendente", "aprovado", "enviado", "entregue", "cancelado")
STATUS_INICIAL_PEDIDO = "pendente"

NOME_PRODUTO_MIN = 2
NOME_PRODUTO_MAX = 200

# (faturamento acima de, taxa de desconto) do maior para o menor
FAIXAS_DESCONTO = ((10000, 0.10), (5000, 0.05), (1000, 0.02))
