const { PAYMENT_STATUS } = require('../services/paymentGateway');

class ReportController {
    constructor({ reportModel }) {
        this.reportModel = reportModel;
    }

    financialReport = async (req, res) => {
        const rows = await this.reportModel.listCourseEnrollments();

        const coursesById = new Map();
        for (const row of rows) {
            if (!coursesById.has(row.course_id)) {
                coursesById.set(row.course_id, { course: row.title, revenue: 0, students: [] });
            }
            if (row.enrollment_id === null) continue;

            const entry = coursesById.get(row.course_id);
            if (row.status === PAYMENT_STATUS.PAID) entry.revenue += row.amount;
            entry.students.push({ student: row.student || 'Unknown', paid: row.amount || 0 });
        }

        res.json([...coursesById.values()]);
    };
}

module.exports = ReportController;
