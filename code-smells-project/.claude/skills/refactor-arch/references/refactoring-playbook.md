# Refactoring Playbook (Phase 3)

Each pattern = **problem → transformation → before/after**. Examples use Python/Flask and Node/Express; apply the same transformation in other stacks. Patterns map to catalog IDs.

Contents: P1 Config · P2 Parameterized queries · P3 Split god file · P4 Thin routes/fat-controller → controller · P5 Remove global state / DI · P6 Password hashing · P7 Central error handler · P8 Dangerous endpoints, write auth & ownership · P9 N+1 · P10 Deduplicate · P11 Async flow · P12 Deprecated APIs · P13 Constants · P14 Sensitive data · P15 Transactions & integrity

---

## P1 — Extract configuration, remove hardcoded secrets (AP-01, AP-11)

**Before**
```python
app.config["SECRET_KEY"] = "minha-chave-super-secreta-123"
app.config["DEBUG"] = True
app.run(host="0.0.0.0", port=5000, debug=True)
```
**After**
```python
# config/settings.py
import os, secrets

class Settings:
    SECRET_KEY = os.environ.get("SECRET_KEY") or secrets.token_hex(32)  # random per boot if unset (dev only)
    DEBUG = os.environ.get("FLASK_DEBUG", "false").lower() == "true"
    HOST = os.environ.get("HOST", "127.0.0.1")
    PORT = int(os.environ.get("PORT", 5000))
    DATABASE_PATH = os.environ.get("DATABASE_PATH", "loja.db")
```
```javascript
// src/config/settings.js
module.exports = {
  port: Number(process.env.PORT || 3000),
  paymentGatewayKey: process.env.PAYMENT_GATEWAY_KEY || '',
  smtpUser: process.env.SMTP_USER || '',
};
```
Also add `.env.example` listing the variables (no real values). Never print secrets.

---

## P2 — Parameterized queries (AP-02)

**Before**
```python
cursor.execute("SELECT * FROM usuarios WHERE email = '" + email + "' AND senha = '" + senha + "'")
cursor.execute("SELECT * FROM produtos WHERE id = " + str(id))
```
**After**
```python
cursor.execute("SELECT * FROM usuarios WHERE email = ?", (email,))
cursor.execute("SELECT * FROM produtos WHERE id = ?", (id,))
# dynamic filters: build the WHERE with placeholders, never with values
clauses, params = ["1=1"], []
if termo:
    clauses.append("(nome LIKE ? OR descricao LIKE ?)"); params += [f"%{termo}%"] * 2
cursor.execute("SELECT * FROM produtos WHERE " + " AND ".join(clauses), params)
```
```javascript
db.get(`SELECT * FROM users WHERE email = ?`, [email], cb);   // already safe; never `${email}`
```

---

## P3 — Split the god file/class into MVC layers (AP-03)

**Before** (one class owns DB + routes + logic)
```javascript
class AppManager {
  constructor() { this.db = new sqlite3.Database(':memory:'); }
  initDb() { /* DDL + seeds */ }
  setupRoutes(app) { app.post('/api/checkout', (req, res) => { /* SQL + rules + response */ }); }
}
```
**After**
```javascript
// views/routes.js
const router = require('express').Router();
router.post('/api/checkout', checkoutController.checkout);
router.get('/api/admin/financial-report', reportController.financialReport);
module.exports = router;

// controllers/checkoutController.js → flow + rules, calls models/services
// models/userModel.js, courseModel.js … → SQL only
// database/connection.js → open DB + schema + seed
// app.js → composition root
```
Procedure: (1) list the responsibilities per function, (2) move SQL to models, (3) move flow to controllers, (4) leave only URL wiring in routes, (5) wire in the composition root, (6) delete the old file.

---

## P4 — Move business logic out of routes into controllers/models (AP-06, AP-14)

**Before** (route does everything, overdue computed inline in 4 places)
```python
@task_bp.route('/tasks', methods=['GET'])
def get_tasks():
    for t in Task.query.all():
        d = {...12 fields...}
        if t.due_date:
            if t.due_date < datetime.utcnow():
                if t.status != 'done' and t.status != 'cancelled': d['overdue'] = True
```
**After**
```python
# models/task.py
def is_overdue(self):
    return bool(self.due_date and self.due_date < utcnow() and self.status not in ('done', 'cancelled'))

# controllers/task_controller.py
def list_tasks():
    return [task.to_dict(include_overdue=True) for task in Task.list_with_relations()]

# routes/task_routes.py
@task_bp.route('/tasks', methods=['GET'])
def get_tasks():
    return jsonify(task_controller.list_tasks()), 200
```
Validation goes into one function shared by create/update, returning domain errors (see P7).

---

## P5 — Remove global state; inject dependencies; app factory (AP-07, AP-09)

**Before**
```python
db_connection = None
def get_db():
    global db_connection
    if db_connection is None:
        db_connection = sqlite3.connect("loja.db", check_same_thread=False)
    return db_connection
```
**After**
```python
# database/connection.py — one connection per request via flask.g
def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(current_app.config["DATABASE_PATH"])
        g.db.row_factory = sqlite3.Row
    return g.db

def close_db(exc=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()

# app.py
def create_app():
    app = Flask(__name__)
    app.config.from_object(Settings)
    app.teardown_appcontext(close_db)
    init_db(app)
    app.register_blueprint(routes)
    register_error_handlers(app)
    return app
```
```javascript
// Node: build collaborators in app.js and pass them down; no module-level mutable exports
const db = await openDatabase(config);
const userModel = new UserModel(db);
app.use(buildRoutes({ checkoutController: new CheckoutController({ userModel, … }) }));
```
Never export primitives that are mutated later (`totalRevenue`): they are copied by value — remove or keep the state in a single owning module with accessors.

---

## P6 — Proper password hashing and tokens (AP-05)

**Before**
```python
self.password = hashlib.md5(pwd.encode()).hexdigest()
```
```javascript
function badCrypto(pwd) { let h = ""; for (let i = 0; i < 10000; i++) h += Buffer.from(pwd).toString('base64').substring(0, 2); return h.substring(0, 10); }
let hash = badCrypto(p || "123456");
```
**After**
```python
from werkzeug.security import generate_password_hash, check_password_hash   # ships with Flask
self.password = generate_password_hash(pwd, method="pbkdf2:sha256")   # salted + slow; scrypt (werkzeug default) needs an OpenSSL build with scrypt, so pick the method explicitly if the runtime may lack it
ok = check_password_hash(self.password, pwd)
# tokens: signed + expiring instead of 'fake-jwt-token-<id>'
from itsdangerous import URLSafeTimedSerializer
token = URLSafeTimedSerializer(current_app.config["SECRET_KEY"]).dumps({"user_id": user.id})
```
```javascript
const crypto = require('crypto');
function hashPassword(pwd) {
  const salt = crypto.randomBytes(16).toString('hex');
  return `${salt}:${crypto.scryptSync(pwd, salt, 64).toString('hex')}`;
}
function verifyPassword(pwd, stored) {
  const [salt, hash] = stored.split(':');
  return crypto.timingSafeEqual(Buffer.from(hash, 'hex'), crypto.scryptSync(pwd, salt, 64));
}
```
Never default a missing password; require it (400). Seed data must store hashes, never plaintext.

---

## P7 — Centralized error handling (AP-15)

**Before**
```python
def criar_produto():
    try: ...
    except Exception as e:
        print("ERRO: " + str(e)); return jsonify({"erro": str(e)}), 500
```
**After**
```python
# middlewares/error_handler.py
class AppError(Exception):
    status = 500
    def __init__(self, message, status=None): super().__init__(message); self.status = status or self.status
class ValidationError(AppError): status = 400
class NotFoundError(AppError): status = 404

def register_error_handlers(app):
    @app.errorhandler(AppError)
    def handle_app_error(err):
        return jsonify({"erro": str(err), "sucesso": False}), err.status
    @app.errorhandler(Exception)
    def handle_unexpected(err):
        app.logger.exception("unhandled error")
        return jsonify({"erro": "Erro interno do servidor", "sucesso": False}), 500
```
```javascript
// middlewares/errorHandler.js (register last)
module.exports = (err, req, res, next) => {
  const status = err.status || 500;
  if (status === 500) console.error(err);
  res.status(status).json({ error: status === 500 ? 'Erro interno' : err.message });
};
// async handlers: wrap with `const wrap = fn => (req,res,next) => fn(req,res,next).catch(next)`
```
Keep the original error JSON keys (`erro` vs `error`) so the contract does not change.

---

## P8 — Remove or protect dangerous endpoints; authenticate writes; check ownership (AP-04)

P8 has three parts and **all three apply whenever AP-04 is reported**. Build the route table first (method, path, who may call it) and implement every row.

### A. Dangerous endpoints (SQL/command execution, reset/debug)

**Before**
```python
@app.route("/admin/query", methods=["POST"])
def executar_query(): cursor.execute(request.get_json()["sql"])
@app.route("/admin/reset-db", methods=["POST"])
def reset_database(): ...DELETE FROM everything...
```
**After**
- Arbitrary SQL/command execution has no safe form → **delete the endpoint** and list it under "Contract changes".
- Destructive admin actions stay only behind explicit auth and an opt-in flag:
```python
def require_admin_token(fn):
    @wraps(fn)
    def wrapper(*a, **kw):
        expected = current_app.config.get("ADMIN_TOKEN")
        if not expected or not hmac.compare_digest(request.headers.get("X-Admin-Token", ""), expected):
            raise AppError("Não autorizado", 403)
        return fn(*a, **kw)
    return wrapper
```
When `ADMIN_TOKEN` is unset the endpoint always answers 403.

### B. Authentication on every write route

Every POST/PUT/PATCH/DELETE must resolve a principal from a **signed** token (P6) and answer **401** without one. Only explicit exceptions stay public: login and self-signup (which must not be able to set `role`/`active`/privilege fields — those need an admin).
```python
# middlewares/auth.py
def current_user():            # None when header missing/invalid/expired
    ...
def login_required(fn):
    @wraps(fn)
    def wrapper(*a, **kw):
        user = current_user()
        if user is None or not user.active:
            raise UnauthorizedError("Autenticação necessária")   # 401
        g.current_user = user
        return fn(*a, **kw)
    return wrapper
def admin_required(fn): ...   # login_required + role check → 403
```
```javascript
const requireAuth = (req, res, next) => {
  const user = verifyBearer(req.headers.authorization);
  if (!user) return next(new HttpError(401, 'Autenticação necessária'));
  req.user = user; next();
};
router.delete('/tasks/:id', requireAuth, controller.remove);
```
Decorate the **route registration** (or the controller entry) so a new write route cannot be added without a visible auth decision.

### C. Ownership (owner-or-admin) on user-owned resources

Authentication is not enough: user A must not edit or delete user B's data, and nobody but an admin may change another account's credentials or privileges.
```python
def ensure_owner_or_admin(owner_id):
    user = g.current_user
    if not user.is_admin() and user.id != owner_id:
        raise ForbiddenError("Sem permissão para este recurso")   # 403

def update_user(user_id):                 # PUT /users/<id> — includes password change
    ensure_owner_or_admin(user_id)        # a user edits only themselves
    if "role" in data or "active" in data: ensure_admin()
def delete_task(task_id):
    task = _get_task_or_404(task_id)
    ensure_owner_or_admin(task.user_id)   # resource without owner → admin only
```
- Run the 401/403 check **before** loading/validating the body, but after route matching, so unauthenticated callers cannot probe which ids exist (still 404 for admins/owners).
- Create routes: force the owner to the caller (default `user_id = current user`); only admins may create on behalf of others.
- Shared resources without an owner (e.g. categories): choose explicitly — authenticated, or admin only for destructive actions — and document it.
- Read routes are out of P8 unless they leak data covered by AP-08.

**Verify (negative tests are mandatory)** for each write route: anonymous → 401; authenticated non-owner → 403; owner → 2xx; admin → 2xx. In particular: anonymous `PUT /users/<admin id>` with `{"password": ...}` must be 401, and a regular user doing the same must be 403. Update seed/smoke scripts to authenticate and list these contract changes.

---

## P9 — Fix N+1 queries (AP-12)

**Before**
```python
for row in cursor.execute("SELECT * FROM pedidos"):
    itens = cursor2.execute("SELECT * FROM itens_pedido WHERE pedido_id = " + str(row["id"]))
    for item in itens:
        prod = cursor3.execute("SELECT nome FROM produtos WHERE id = " + str(item["produto_id"]))
```
**After** (one JOIN, group in memory)
```python
rows = cursor.execute("""
  SELECT p.id, p.usuario_id, p.status, p.total, p.criado_em,
         i.produto_id, i.quantidade, i.preco_unitario, pr.nome AS produto_nome
  FROM pedidos p
  LEFT JOIN itens_pedido i ON i.pedido_id = p.id
  LEFT JOIN produtos pr ON pr.id = i.produto_id
  ORDER BY p.id""").fetchall()
pedidos = {}
for r in rows:
    pedido = pedidos.setdefault(r["id"], {..., "itens": []})
    if r["produto_id"] is not None:
        pedido["itens"].append({...})
```
ORM: eager-load (`joinedload`/`selectinload`) or aggregate with `GROUP BY` (`db.session.query(Task.user_id, func.count()).group_by(Task.user_id)`) instead of lazy loops.

---

## P10 — Deduplicate code (AP-13)

**Before**: the same overdue check pasted in 5 handlers; same row→dict mapping repeated 5 times.
**After**: one definition, reused.
```python
def serialize_produto(row):
    return {k: row[k] for k in ("id", "nome", "descricao", "preco", "estoque", "categoria", "ativo", "criado_em")}
produtos = [serialize_produto(r) for r in rows]
```
Shared validators live in `utils/validators.py` or controller helpers (`validate_produto_payload(data)`) and are used by both create and update. Delete helper functions that remain unused.

---

## P11 — Callback hell → async/await (AP-16)

**Before**
```javascript
this.db.all("SELECT * FROM courses", [], (err, courses) => {
  courses.forEach(c => this.db.all("SELECT * FROM enrollments WHERE course_id = ?", [c.id], (err, enrs) => {
    enrs.forEach(enr => this.db.get("SELECT ...", [enr.user_id], (err, user) => { /* counters… */ }));
  }));
});
```
**After**
```javascript
// database/connection.js — promisified helpers
const run = (sql, p = []) => new Promise((res, rej) => db.run(sql, p, function (e) { e ? rej(e) : res(this); }));
const get = (sql, p = []) => new Promise((res, rej) => db.get(sql, p, (e, r) => e ? rej(e) : res(r)));
const all = (sql, p = []) => new Promise((res, rej) => db.all(sql, p, (e, r) => e ? rej(e) : res(r)));

// model: one JOIN instead of 3 nested levels (also fixes N+1 and non-deterministic order)
const rows = await all(`SELECT c.id, c.title, u.name, p.amount, p.status
                        FROM courses c LEFT JOIN enrollments e ON e.course_id = c.id
                        LEFT JOIN users u ON u.id = e.user_id
                        LEFT JOIN payments p ON p.enrollment_id = e.id ORDER BY c.id, e.id`);
```

---

## P12 — Replace deprecated APIs (AP-17)

| Before | After |
|---|---|
| `datetime.utcnow()` | `datetime.now(timezone.utc)` — if the DB stores naive datetimes use a helper `def utcnow(): return datetime.now(timezone.utc).replace(tzinfo=None)` |
| `Task.query.get(id)` | `db.session.get(Task, id)` |
| `default=datetime.utcnow` (column) | `default=utcnow` (the helper above) |
| `new Buffer(x)` | `Buffer.from(x)` |
| `ioutil.ReadAll` (Go) | `io.ReadAll` |
| `print(...)` | `logging.getLogger(__name__).info(...)` |

Apply with a project-wide search; verify tests/boot after the change (aware vs naive datetime comparisons raise `TypeError`).

---

## P13 — Replace magic numbers/strings with named constants (AP-18)

**Before**
```python
if faturamento > 10000: desconto = faturamento * 0.1
elif faturamento > 5000: desconto = faturamento * 0.05
elif faturamento > 1000: desconto = faturamento * 0.02
if novo_status not in ["pendente", "aprovado", "enviado", "entregue", "cancelado"]: ...
```
**After**
```python
# config/settings.py
DISCOUNT_TIERS = ((10000, 0.10), (5000, 0.05), (1000, 0.02))   # (threshold, rate), highest first
ORDER_STATUSES = ("pendente", "aprovado", "enviado", "entregue", "cancelado")

def discount_for(revenue):
    return next((revenue * rate for threshold, rate in DISCOUNT_TIERS if revenue > threshold), 0)
```

---

## P14 — Stop exposing sensitive data (AP-08)

**Before**
```python
def to_dict(self): return {..., 'password': self.password}
return jsonify({"status": "ok", "secret_key": "minha-chave...", "debug": True, "db_path": "loja.db"})
print(f"Processando cartão {cc} na chave {config.paymentGatewayKey}")
```
**After**
```python
def to_dict(self): return {"id": self.id, "name": self.name, "email": self.email, "role": self.role}   # no password
return jsonify({"status": "ok", "database": "connected", "counts": counts})
```
```javascript
logger.info(`Processando pagamento do curso ${courseId}`);   // never log card numbers, keys, tokens
```
Also: do not return `str(exception)` to clients; log it and return a generic message (P7).

---

## P15 — Transactions and referential integrity (AP-10)

**Before**: order insert, item inserts and stock decrement done as separate commits/with early returns; deleting a user leaves enrollments and payments.
**After**
```python
def criar_pedido(usuario_id, itens):
    db = get_db()
    try:
        db.execute("BEGIN")
        total = 0
        for item in itens:
            produto = db.execute("SELECT id, nome, preco, estoque FROM produtos WHERE id = ?", (item["produto_id"],)).fetchone()
            if produto is None:
                raise NotFoundError(f"Produto {item['produto_id']} não encontrado")
            if produto["estoque"] < item["quantidade"]:
                raise ValidationError(f"Estoque insuficiente para {produto['nome']}")
            ...
        db.commit()
    except Exception:
        db.rollback()
        raise
```
```javascript
// delete parent + children atomically
await db.transaction(async tx => {
  await tx.run('DELETE FROM payments WHERE enrollment_id IN (SELECT id FROM enrollments WHERE user_id = ?)', [id]);
  await tx.run('DELETE FROM enrollments WHERE user_id = ?', [id]);
  await tx.run('DELETE FROM users WHERE id = ?', [id]);
});
```
In single-connection drivers serialize transactions (a small promise-queue mutex) so concurrent requests do not interleave inside one transaction.
