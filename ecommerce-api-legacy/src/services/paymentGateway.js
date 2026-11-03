const PAYMENT_STATUS = Object.freeze({ PAID: 'PAID', DENIED: 'DENIED' });

// Simulação do gateway: cartões iniciados em "4" são aprovados.
const APPROVED_CARD_PREFIX = '4';

class PaymentGateway {
    constructor({ apiKey, logger }) {
        this.apiKey = apiKey;
        this.logger = logger;
    }

    charge({ cardNumber, amount }) {
        // o número do cartão e a chave nunca são logados
        this.logger.info(`Processando pagamento de ${amount}`);
        return cardNumber.startsWith(APPROVED_CARD_PREFIX) ? PAYMENT_STATUS.PAID : PAYMENT_STATUS.DENIED;
    }
}

module.exports = { PaymentGateway, PAYMENT_STATUS };
