from werkzeug.security import check_password_hash, generate_password_hash


def hash_senha(senha):
    # pbkdf2 funciona em qualquer build do Python (scrypt depende do OpenSSL)
    return generate_password_hash(senha, method="pbkdf2:sha256")


def verificar_senha(senha_hash, senha):
    return check_password_hash(senha_hash, senha)
