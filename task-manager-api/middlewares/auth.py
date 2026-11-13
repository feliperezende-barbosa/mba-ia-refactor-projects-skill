from functools import wraps

from flask import g, request

from models.user import User
from services.auth_service import verify_token
from utils.errors import ForbiddenError, UnauthorizedError


def current_user():
    """Usuário do token Bearer, ou None se ausente/inválido/expirado."""
    if "current_user" not in g:
        header = request.headers.get("Authorization", "")
        user_id = verify_token(header[len("Bearer "):]) if header.startswith("Bearer ") else None
        g.current_user = User.find(user_id) if user_id else None
    return g.current_user


def ensure_authenticated():
    user = current_user()
    if user is None or not user.active:
        raise UnauthorizedError("Autenticação necessária")
    return user


def ensure_admin():
    user = ensure_authenticated()
    if not user.is_admin():
        raise ForbiddenError("Apenas administradores podem executar esta ação")
    return user


def ensure_owner_or_admin(owner_id):
    """Recurso sem dono (owner_id None) só pode ser alterado por admin."""
    user = ensure_authenticated()
    if not user.is_admin() and (owner_id is None or user.id != owner_id):
        raise ForbiddenError("Sem permissão para alterar este recurso")
    return user


def login_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        ensure_authenticated()
        return fn(*args, **kwargs)
    return wrapper


def admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        ensure_admin()
        return fn(*args, **kwargs)
    return wrapper
