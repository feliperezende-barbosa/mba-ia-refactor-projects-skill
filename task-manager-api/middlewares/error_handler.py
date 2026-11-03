from flask import jsonify
from werkzeug.exceptions import HTTPException

from utils.errors import AppError


def register_error_handlers(app):
    @app.errorhandler(AppError)
    def handle_app_error(err):
        return jsonify({'error': str(err)}), err.status

    @app.errorhandler(HTTPException)
    def handle_http_error(err):
        return jsonify({'error': err.description}), err.code

    @app.errorhandler(Exception)
    def handle_unexpected(err):
        app.logger.exception('Erro não tratado: %s', err)
        return jsonify({'error': 'Erro interno'}), 500
