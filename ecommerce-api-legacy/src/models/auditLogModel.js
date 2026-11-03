class AuditLogModel {
    constructor(db) {
        this.db = db;
    }

    record(action, db = this.db) {
        return db.run("INSERT INTO audit_logs (action, created_at) VALUES (?, datetime('now'))", [action]);
    }
}

module.exports = AuditLogModel;
