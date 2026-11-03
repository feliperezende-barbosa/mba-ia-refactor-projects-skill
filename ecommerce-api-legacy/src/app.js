const express = require('express');
const settings = require('./config/settings');
const logger = require('./utils/logger');
const Database = require('./database/connection');
const { initDatabase } = require('./database/schema');
const UserModel = require('./models/userModel');
const CourseModel = require('./models/courseModel');
const EnrollmentModel = require('./models/enrollmentModel');
const PaymentModel = require('./models/paymentModel');
const AuditLogModel = require('./models/auditLogModel');
const ReportModel = require('./models/reportModel');
const { PaymentGateway } = require('./services/paymentGateway');
const CheckoutController = require('./controllers/checkoutController');
const ReportController = require('./controllers/reportController');
const UserController = require('./controllers/userController');
const buildRoutes = require('./views/routes');
const errorHandler = require('./middlewares/errorHandler');

async function createApp() {
    const db = new Database(':memory:');
    await initDatabase(db);

    const userModel = new UserModel(db);
    const paymentGateway = new PaymentGateway({ apiKey: settings.paymentGatewayKey, logger });

    const routes = buildRoutes({
        adminToken: settings.adminToken,
        checkoutController: new CheckoutController({
            db,
            userModel,
            courseModel: new CourseModel(db),
            enrollmentModel: new EnrollmentModel(db),
            paymentModel: new PaymentModel(db),
            auditLogModel: new AuditLogModel(db),
            paymentGateway,
            logger,
        }),
        reportController: new ReportController({ reportModel: new ReportModel(db) }),
        userController: new UserController({ userModel, logger }),
    });

    const app = express();
    app.use(express.json());
    app.use(routes);
    app.use(errorHandler);
    return app;
}

if (require.main === module) {
    createApp()
        .then((app) => app.listen(settings.port, () => logger.info(`LMS API rodando na porta ${settings.port}`)))
        .catch((err) => {
            logger.error('Falha ao iniciar a aplicação:', err);
            process.exit(1);
        });
}

module.exports = { createApp };
