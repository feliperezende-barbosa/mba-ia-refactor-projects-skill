class UserModel {
    constructor(db) {
        this.db = db;
    }

    findByEmail(email, db = this.db) {
        return db.get('SELECT id, name, email FROM users WHERE email = ?', [email]);
    }

    async create({ name, email, passwordHash }, db = this.db) {
        const { lastID } = await db.run('INSERT INTO users (name, email, pass) VALUES (?, ?, ?)', [name, email, passwordHash]);
        return lastID;
    }

    // Remove o usuário e tudo que depende dele (pagamentos → matrículas → usuário).
    deleteWithDependents(userId) {
        return this.db.transaction(async (tx) => {
            await tx.run(
                'DELETE FROM payments WHERE enrollment_id IN (SELECT id FROM enrollments WHERE user_id = ?)',
                [userId],
            );
            await tx.run('DELETE FROM enrollments WHERE user_id = ?', [userId]);
            const { changes } = await tx.run('DELETE FROM users WHERE id = ?', [userId]);
            return changes > 0;
        });
    }
}

module.exports = UserModel;
