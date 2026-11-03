import hmac
from functools import wraps

from flask import current_app, jsonify, request

from utils.errors import AppError, ForbiddenError


def admin_required(fn):
    """Exige o header X-Admin-Token igual a ADMIN_TOKEN; sem ADMIN_TOKEN configurado, nega sempre."""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        esperado = current_app.config.get("ADMIN_TOKEN")
        recebido = request.headers.get("X-Admin-Token", "")
        if not esperado or not hmac.compare_digest(recebido, esperado):
            raise ForbiddenError("Não autorizado")
        return fn(*args, **kwargs)
    return wrapper


def register_error_handlers(app):
    @app.errorhandler(AppError)
    def handle_app_error(erro):
        return jsonify({"erro": str(erro), "sucesso": False}), erro.status

    @app.errorhandler(404)
    def handle_not_found(_erro):
        return jsonify({"erro": "Recurso não encontrado", "sucesso": False}), 404

    @app.errorhandler(405)
    def handle_method_not_allowed(_erro):
        return jsonify({"erro": "Método não permitido", "sucesso": False}), 405

    @app.errorhandler(Exception)
    def handle_unexpected(erro):
        app.logger.exception("Erro não tratado: %s", erro)
        return jsonify({"erro": "Erro interno do servidor", "sucesso": False}), 500
