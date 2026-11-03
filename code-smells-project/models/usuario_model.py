from database.connection import get_db

# `senha` nunca é serializada
CAMPOS_PUBLICOS = ("id", "nome", "email", "tipo", "criado_em")


def serializar(row):
    return {campo: row[campo] for campo in CAMPOS_PUBLICOS}


def listar():
    rows = get_db().execute("SELECT * FROM usuarios").fetchall()
    return [serializar(r) for r in rows]


def buscar_por_id(usuario_id):
    row = get_db().execute("SELECT * FROM usuarios WHERE id = ?", (usuario_id,)).fetchone()
    return serializar(row) if row else None


def buscar_credenciais_por_email(email):
    """Retorna a linha completa (inclui o hash) apenas para uso interno na autenticação."""
    return get_db().execute("SELECT * FROM usuarios WHERE email = ?", (email,)).fetchone()


def criar(nome, email, senha_hash, tipo="cliente"):
    cursor = get_db().execute(
        "INSERT INTO usuarios (nome, email, senha, tipo) VALUES (?, ?, ?, ?)",
        (nome, email, senha_hash, tipo),
    )
    return cursor.lastrowid
