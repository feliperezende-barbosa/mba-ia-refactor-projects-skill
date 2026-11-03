const { ValidationError, NotFoundError } = require('../utils/errors');

class UserController {
    constructor({ userModel, logger }) {
        this.userModel = userModel;
        this.logger = logger;
    }

    deleteUser = async (req, res) => {
        const userId = Number(req.params.id);
        if (!Number.isInteger(userId) || userId <= 0) throw new ValidationError('ID inválido');

        const deleted = await this.userModel.deleteWithDependents(userId);
        if (!deleted) throw new NotFoundError('Usuário não encontrado');

        this.logger.info(`Usuário ${userId} removido junto com matrículas e pagamentos`);
        res.send('Usuário deletado com sucesso.');
    };
}

module.exports = UserController;
