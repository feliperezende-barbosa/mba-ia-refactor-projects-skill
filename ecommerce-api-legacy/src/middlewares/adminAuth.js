const crypto = require('crypto');
const { ForbiddenError } = require('../utils/errors');

// Exige o header X-Admin-Token igual a ADMIN_TOKEN; sem ADMIN_TOKEN configurado, nega sempre.
function adminAuth(adminToken) {
    return (req, res, next) => {
        const received = Buffer.from(String(req.get('X-Admin-Token') || ''));
        const expected = Buffer.from(adminToken || '');
        const valid = expected.length > 0
            && received.length === expected.length
            && crypto.timingSafeEqual(received, expected);
        next(valid ? undefined : new ForbiddenError());
    };
}

module.exports = adminAuth;
