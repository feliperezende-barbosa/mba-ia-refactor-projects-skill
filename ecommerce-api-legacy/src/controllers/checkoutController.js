const { ValidationError, NotFoundError } = require('../utils/errors');
const { hashPassword } = require('../services/passwordService');
const { PAYMENT_STATUS } = require('../services/paymentGateway');

class CheckoutController {
    constructor({ db, userModel, courseModel, enrollmentModel, paymentModel, auditLogModel, paymentGateway, logger }) {
        this.db = db;
        this.userModel = userModel;
        this.courseModel = courseModel;
        this.enrollmentModel = enrollmentModel;
        this.paymentModel = paymentModel;
        this.auditLogModel = auditLogModel;
        this.paymentGateway = paymentGateway;
        this.logger = logger;
    }

    // Os nomes dos campos do JSON (usr, eml, pwd, c_id, card) são o contrato público da API.
    checkout = async (req, res) => {
        const { usr: name, eml: email, pwd: password, c_id: courseId, card: cardNumber } = req.body || {};

        if (!name || !email || !courseId || !cardNumber) throw new ValidationError('Bad Request');
        if (![name, email, cardNumber].every((v) => typeof v === 'string')) throw new ValidationError('Bad Request');

        const course = await this.courseModel.findActiveById(courseId);
        if (!course) throw new NotFoundError('Curso não encontrado');

        const existingUser = await this.userModel.findByEmail(email);
        if (!existingUser && !password) throw new ValidationError('Senha é obrigatória para novos usuários');

        const paymentStatus = this.paymentGateway.charge({ cardNumber, amount: course.price });
        if (paymentStatus !== PAYMENT_STATUS.PAID) throw new ValidationError('Pagamento recusado');

        const passwordHash = existingUser ? null : await hashPassword(String(password));

        const enrollmentId = await this.db.transaction(async (tx) => {
            const userId = existingUser
                ? existingUser.id
                : await this.userModel.create({ name, email, passwordHash }, tx);
            const newEnrollmentId = await this.enrollmentModel.create({ userId, courseId }, tx);
            await this.paymentModel.create({ enrollmentId: newEnrollmentId, amount: course.price, status: paymentStatus }, tx);
            await this.auditLogModel.record(`Checkout curso ${courseId} por ${userId}`, tx);
            return newEnrollmentId;
        });

        this.logger.info(`Checkout concluído: curso ${courseId}, matrícula ${enrollmentId}`);
        res.status(200).json({ msg: 'Sucesso', enrollment_id: enrollmentId });
    };
}

module.exports = CheckoutController;
