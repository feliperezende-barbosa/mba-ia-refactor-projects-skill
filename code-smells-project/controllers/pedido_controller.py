from flask import jsonify, request

from config.settings import STATUS_PEDIDO
from models import pedido_model
from services import notification_service
from utils.errors import NotFoundError, ValidationError
from utils.validators import exigir_json, validar_itens_pedido


def criar_pedido():
    dados = exigir_json(request.get_json(silent=True))
    usuario_id = dados.get("usuario_id")
    if not usuario_id:
        raise ValidationError("Usuario ID é obrigatório")
    itens = validar_itens_pedido(dados.get("itens", []))

    resultado = pedido_model.criar(usuario_id, itens)
    notification_service.pedido_criado(resultado["pedido_id"], usuario_id)
    return jsonify({"dados": resultado, "sucesso": True, "mensagem": "Pedido criado com sucesso"}), 201


def listar_pedidos_usuario(usuario_id):
    return jsonify({"dados": pedido_model.listar_por_usuario(usuario_id), "sucesso": True}), 200


def listar_todos_pedidos():
    return jsonify({"dados": pedido_model.listar_todos(), "sucesso": True}), 200


def atualizar_status_pedido(pedido_id):
    dados = request.get_json(silent=True)
    novo_status = dados.get("status", "") if isinstance(dados, dict) else ""
    if novo_status not in STATUS_PEDIDO:
        raise ValidationError("Status inválido")

    if not pedido_model.atualizar_status(pedido_id, novo_status):
        raise NotFoundError("Pedido não encontrado")
    notification_service.status_pedido_alterado(pedido_id, novo_status)
    return jsonify({"sucesso": True, "mensagem": "Status atualizado"}), 200
