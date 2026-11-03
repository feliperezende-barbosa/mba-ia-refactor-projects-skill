const settings = {
    port: Number(process.env.PORT || 3000),
    environment: process.env.NODE_ENV || 'development',
    // Segredos vêm exclusivamente do ambiente; sem valor padrão no código.
    paymentGatewayKey: process.env.PAYMENT_GATEWAY_KEY || '',
    adminToken: process.env.ADMIN_TOKEN || '',
};

module.exports = settings;
