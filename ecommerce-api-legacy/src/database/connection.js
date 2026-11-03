const sqlite3 = require('sqlite3');

// Encapsula o driver (API de callbacks) em Promises e serializa transações,
// já que há uma única conexão compartilhada.
class Database {
    constructor(location = ':memory:') {
        this.raw = new sqlite3.Database(location);
        this.queue = Promise.resolve();
    }

    run(sql, params = []) {
        return new Promise((resolve, reject) => {
            this.raw.run(sql, params, function onRun(err) {
                if (err) return reject(err);
                resolve({ lastID: this.lastID, changes: this.changes });
            });
        });
    }

    get(sql, params = []) {
        return new Promise((resolve, reject) => {
            this.raw.get(sql, params, (err, row) => (err ? reject(err) : resolve(row)));
        });
    }

    all(sql, params = []) {
        return new Promise((resolve, reject) => {
            this.raw.all(sql, params, (err, rows) => (err ? reject(err) : resolve(rows)));
        });
    }

    transaction(work) {
        const result = this.queue.then(async () => {
            await this.run('BEGIN');
            try {
                const output = await work(this);
                await this.run('COMMIT');
                return output;
            } catch (err) {
                await this.run('ROLLBACK');
                throw err;
            }
        });
        this.queue = result.catch(() => {});
        return result;
    }

    close() {
        return new Promise((resolve, reject) => this.raw.close((err) => (err ? reject(err) : resolve())));
    }
}

module.exports = Database;
