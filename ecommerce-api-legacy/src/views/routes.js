const express = require('express');
const asyncHandler = require('../middlewares/asyncHandler');
const adminAuth = require('../middlewares/adminAuth');

function buildRoutes({ checkoutController, reportController, userController, adminToken }) {
    const router = express.Router();
    const requireAdmin = adminAuth(adminToken);

    router.post('/api/checkout', asyncHandler(checkoutController.checkout));
    router.get('/api/admin/financial-report', requireAdmin, asyncHandler(reportController.financialReport));
    router.delete('/api/users/:id', requireAdmin, asyncHandler(userController.deleteUser));

    return router;
}

module.exports = buildRoutes;
