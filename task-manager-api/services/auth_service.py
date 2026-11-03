from flask import current_app
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer


def _serializer():
    return URLSafeTimedSerializer(current_app.config["SECRET_KEY"], salt="task-manager-auth")


def generate_token(user):
    return _serializer().dumps({"user_id": user.id})


def verify_token(token):
    """Retorna o id do usuário do token ou None se for inválido/expirado."""
    try:
        data = _serializer().loads(token, max_age=current_app.config["TOKEN_MAX_AGE_SECONDS"])
    except (BadSignature, SignatureExpired):
        return None
    return data.get("user_id")
