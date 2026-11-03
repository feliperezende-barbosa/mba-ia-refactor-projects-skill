const logger = require('../utils/logger');
const { AppError } = require('../utils/errors');

// Mantém o contrato original: erros em texto simples com o mesmo status HTTP.
// eslint-disable-next-line no-unused-vars
function errorHandler(err, req, res, next) {
    if (err instanceof AppError) {
        return res.status(err.status).send(err.message);
    }
    if (err && err.type === 'entity.parse.failed') {
        return res.status(400).send('Bad Request');
    }
    logger.error('Erro não tratado:', err);
    return res.status(500).send('Erro interno do servidor');
}

module.exports = errorHandler;
