import logging

from flask import jsonify, request

from models import produto_model
from utils.errors import NotFoundError, ValidationError
from utils.validators import validar_produto

logger = logging.getLogger(__name__)


def _obter_ou_404(produto_id):
    produto = produto_model.buscar_por_id(produto_id)
    if not produto:
        raise NotFoundError("Produto não encontrado")
    return produto


def listar_produtos():
    produtos = produto_model.listar()
    return jsonify({"dados": produtos, "sucesso": True}), 200


def buscar_produto(id):
    return jsonify({"dados": _obter_ou_404(id), "sucesso": True}), 200


def criar_produto():
    campos = validar_produto(request.get_json(silent=True))
    produto_id = produto_model.criar(**campos)
    logger.info("Produto criado com ID %s", produto_id)
    return jsonify({"dados": {"id": produto_id}, "sucesso": True, "mensagem": "Produto criado"}), 201


def atualizar_produto(id):
    _obter_ou_404(id)
    campos = validar_produto(request.get_json(silent=True))
    produto_model.atualizar(id, **campos)
    return jsonify({"sucesso": True, "mensagem": "Produto atualizado"}), 200


def deletar_produto(id):
    _obter_ou_404(id)
    produto_model.deletar(id)
    logger.info("Produto %s deletado", id)
    return jsonify({"sucesso": True, "mensagem": "Produto deletado"}), 200


def _parse_preco(valor, nome):
    if valor in (None, ""):
        return None
    try:
        return float(valor)
    except ValueError:
        raise ValidationError(f"Parâmetro {nome} inválido")


def buscar_produtos():
    termo = request.args.get("q", "")
    categoria = request.args.get("categoria")
    preco_min = _parse_preco(request.args.get("preco_min"), "preco_min")
    preco_max = _parse_preco(request.args.get("preco_max"), "preco_max")

    resultados = produto_model.buscar(termo, categoria, preco_min, preco_max)
    return jsonify({"dados": resultados, "total": len(resultados), "sucesso": True}), 200
