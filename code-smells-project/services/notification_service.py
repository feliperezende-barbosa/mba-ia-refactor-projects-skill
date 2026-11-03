import logging

logger = logging.getLogger("notificacoes")


def pedido_criado(pedido_id, usuario_id):
    logger.info("EMAIL: pedido %s criado para usuario %s", pedido_id, usuario_id)
    logger.info("SMS: pedido %s recebido", pedido_id)
    logger.info("PUSH: novo pedido %s recebido pelo sistema", pedido_id)


def status_pedido_alterado(pedido_id, novo_status):
    if novo_status == "aprovado":
        logger.info("Pedido %s aprovado: preparar envio", pedido_id)
    elif novo_status == "cancelado":
        logger.info("Pedido %s cancelado: devolver estoque", pedido_id)
