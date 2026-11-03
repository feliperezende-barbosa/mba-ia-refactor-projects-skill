from flask import jsonify

from config.settings import FAIXAS_DESCONTO
from models import pedido_model


def calcular_desconto(faturamento):
    return next((faturamento * taxa for limite, taxa in FAIXAS_DESCONTO if faturamento > limite), 0)


def relatorio_vendas():
    resumo = pedido_model.resumo_vendas()
    faturamento = resumo["faturamento"]
    total_pedidos = resumo["total_pedidos"]
    desconto = calcular_desconto(faturamento)

    relatorio = {
        "total_pedidos": total_pedidos,
        "faturamento_bruto": round(faturamento, 2),
        "desconto_aplicavel": round(desconto, 2),
        "faturamento_liquido": round(faturamento - desconto, 2),
        "pedidos_pendentes": resumo["pendentes"],
        "pedidos_aprovados": resumo["aprovados"],
        "pedidos_cancelados": resumo["cancelados"],
        "ticket_medio": round(faturamento / total_pedidos, 2) if total_pedidos > 0 else 0,
    }
    return jsonify({"dados": relatorio, "sucesso": True}), 200
