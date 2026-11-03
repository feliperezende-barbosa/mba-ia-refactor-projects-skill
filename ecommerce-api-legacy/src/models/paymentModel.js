class PaymentModel {
    constructor(db) {
        this.db = db;
    }

    create({ enrollmentId, amount, status }, db = this.db) {
        return db.run('INSERT INTO payments (enrollment_id, amount, status) VALUES (?, ?, ?)', [enrollmentId, amount, status]);
    }
}

module.exports = PaymentModel;
