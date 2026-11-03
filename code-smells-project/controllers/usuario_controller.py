import logging

from flask import jsonify, request

from models import usuario_model
from services.password_service import hash_senha, verificar_senha
from utils.errors import NotFoundError, UnauthorizedError, ValidationError
from utils.validators import validar_usuario

logger = logging.getLogger(__name__)


def listar_usuarios():
    return jsonify({"dados": usuario_model.listar(), "sucesso": True}), 200


def buscar_usuario(id):
    usuario = usuario_model.buscar_por_id(id)
    if not usuario:
        raise NotFoundError("Usuário não encontrado")
    return jsonify({"dados": usuario, "sucesso": True}), 200


def criar_usuario():
    nome, email, senha = validar_usuario(request.get_json(silent=True))
    usuario_id = usuario_model.criar(nome, email, hash_senha(senha))
    logger.info("Usuário criado: id=%s", usuario_id)
    return jsonify({"dados": {"id": usuario_id}, "sucesso": True}), 201


def login():
    dados = request.get_json(silent=True)
    email = dados.get("email", "") if isinstance(dados, dict) else ""
    senha = dados.get("senha", "") if isinstance(dados, dict) else ""
    if not email or not senha:
        raise ValidationError("Email e senha são obrigatórios")

    credenciais = usuario_model.buscar_credenciais_por_email(email)
    if not credenciais or not verificar_senha(credenciais["senha"], senha):
        logger.info("Login falhou")
        raise UnauthorizedError("Email ou senha inválidos")

    logger.info("Login bem-sucedido: usuario_id=%s", credenciais["id"])
    usuario = {k: credenciais[k] for k in ("id", "nome", "email", "tipo")}
    return jsonify({"dados": usuario, "sucesso": True, "mensagem": "Login OK"}), 200
