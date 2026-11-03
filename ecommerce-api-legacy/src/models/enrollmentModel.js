class EnrollmentModel {
    constructor(db) {
        this.db = db;
    }

    async create({ userId, courseId }, db = this.db) {
        const { lastID } = await db.run('INSERT INTO enrollments (user_id, course_id) VALUES (?, ?)', [userId, courseId]);
        return lastID;
    }
}

module.exports = EnrollmentModel;
