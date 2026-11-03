from numbers import Real

from config.settings import (
    CATEGORIA_PADRAO,
    CATEGORIAS_VALIDAS,
    NOME_PRODUTO_MAX,
    NOME_PRODUTO_MIN,
)
from utils.errors import ValidationError


def exigir_json(dados):
    if not isinstance(dados, dict) or not dados:
        raise ValidationError("Dados inválidos")
    return dados


def _numero(valor):
    return isinstance(valor, Real) and not isinstance(valor, bool)


def validar_produto(dados):
    """Valida o payload de criação/atualização de produto e devolve os campos normalizados."""
    exigir_json(dados)
    for campo, mensagem in (("nome", "Nome é obrigatório"), ("preco", "Preço é obrigatório"), ("estoque", "Estoque é obrigatório")):
        if campo not in dados:
            raise ValidationError(mensagem)

    nome, preco, estoque = dados["nome"], dados["preco"], dados["estoque"]
    descricao = dados.get("descricao", "")
    categoria = dados.get("categoria", CATEGORIA_PADRAO)

    if not isinstance(nome, str) or not isinstance(descricao, str):
        raise ValidationError("Nome e descrição devem ser texto")
    if not _numero(preco):
        raise ValidationError("Preço inválido")
    if not _numero(estoque) or int(estoque) != estoque:
        raise ValidationError("Estoque inválido")
    if preco < 0:
        raise ValidationError("Preço não pode ser negativo")
    if estoque < 0:
        raise ValidationError("Estoque não pode ser negativo")
    if len(nome) < NOME_PRODUTO_MIN:
        raise ValidationError("Nome muito curto")
    if len(nome) > NOME_PRODUTO_MAX:
        raise ValidationError("Nome muito longo")
    if categoria not in CATEGORIAS_VALIDAS:
        raise ValidationError("Categoria inválida. Válidas: " + str(list(CATEGORIAS_VALIDAS)))

    return {
        "nome": nome,
        "descricao": descricao,
        "preco": preco,
        "estoque": int(estoque),
        "categoria": categoria,
    }


def validar_usuario(dados):
    exigir_json(dados)
    nome, email, senha = dados.get("nome", ""), dados.get("email", ""), dados.get("senha", "")
    if not nome or not email or not senha:
        raise ValidationError("Nome, email e senha são obrigatórios")
    if not all(isinstance(v, str) for v in (nome, email, senha)):
        raise ValidationError("Nome, email e senha devem ser texto")
    return nome, email, senha


def validar_itens_pedido(itens):
    if not itens or not isinstance(itens, list):
        raise ValidationError("Pedido deve ter pelo menos 1 item")
    for item in itens:
        if not isinstance(item, dict):
            raise ValidationError("Item do pedido inválido")
        produto_id, quantidade = item.get("produto_id"), item.get("quantidade")
        if not isinstance(produto_id, int) or isinstance(produto_id, bool):
            raise ValidationError("Item do pedido inválido: produto_id")
        if not isinstance(quantidade, int) or isinstance(quantidade, bool) or quantidade <= 0:
            raise ValidationError("Item do pedido inválido: quantidade deve ser um inteiro positivo")
    return itens
