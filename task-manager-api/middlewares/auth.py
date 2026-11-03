from functools import wraps

from flask import request

from models.user import User
from services.auth_service import verify_token
from utils.errors import ForbiddenError, UnauthorizedError


def current_user():
    header = request.headers.get("Authorization", "")
    if not header.startswith("Bearer "):
        return None
    user_id = verify_token(header[len("Bearer "):])
    return User.find(user_id) if user_id else None


def ensure_admin():
    user = current_user()
    if user is None or not user.active:
        raise UnauthorizedError("Autenticação necessária")
    if not user.is_admin():
        raise ForbiddenError("Apenas administradores podem executar esta ação")
    return user


def admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        ensure_admin()
        return fn(*args, **kwargs)
    return wrapper
