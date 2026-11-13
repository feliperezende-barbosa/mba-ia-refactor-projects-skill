# Anti-Pattern Catalog (Phase 2)

Severity scale (MVC + SOLID based):

- **CRITICAL** — Severe architecture or security flaws: hardcoded credentials, SQL injection, exposure of sensitive data, god class/file that mixes DB + business logic + routing, destructive/arbitrary-execution endpoints without auth.
- **HIGH** — Strong MVC/SOLID violations that make maintenance and testing very hard: business logic inside controllers/routes, tight coupling without dependency injection, mutable global state, non-atomic multi-step writes.
- **MEDIUM** — Standardization problems, duplication, moderate performance issues: N+1 queries, missing/inconsistent validation, duplicated code, ad-hoc error handling, deprecated APIs.
- **LOW** — Readability: poor naming, magic numbers/strings, `print`/`console.log` instead of a logger, dead code, unused imports.

How to use: for each entry, search for the **signals** (grep is a good triage), open the code to confirm, then record `file:start-end`. Signals are language-agnostic; the "stack examples" column shows what they look like in the stacks seen so far, but apply the same reasoning to any language.

---

## CRITICAL

### AP-01 Hardcoded credentials / secrets
- **Signals**: string literals assigned to names matching `secret|key|password|passwd|pwd|token|api_key|smtp|dsn|connection string`; DB/SMTP/payment credentials in source; `SECRET_KEY = "..."`; seeded default passwords outside seed data.
- **Stack examples**: `app.config["SECRET_KEY"] = "abc"` (Flask); `const config = { dbPass: "..." , paymentGatewayKey: "pk_live_..." }` (Node); `self.email_password = 'senha123'`.
- **Impact**: credentials leak via VCS/logs; cannot rotate per environment.
- **Fix**: playbook P1.

### AP-02 SQL injection (string-built queries)
- **Signals**: SQL text built with `+`, f-strings, `%`, `.format`, template literals including request-derived values; `execute("..." + x)`; `LIKE '%" + term + "%'`; `db.query(\`... ${req.params.id}\`)`. Parameter placeholders (`?`, `%s`, `$1`, `:name`) are the safe form.
- **Impact**: auth bypass, data exfiltration, data destruction.
- **Fix**: playbook P2.

### AP-03 God Class / God File (no layer separation)
- **Signals**: a single file/class containing routing + validation + SQL + business rules + formatting; file > ~250 lines with > 3 responsibilities; a class named `Manager|Handler|Util|Service` that defines routes AND creates the DB AND executes queries; every route handler inlined in one `setupRoutes`.
- **Impact**: impossible to test in isolation; any change affects everything.
- **Fix**: playbook P3.

### AP-04 Unprotected dangerous endpoints / missing authentication and ownership checks
- **Signals**:
  - routes such as `/admin/*`, `/reset`, `/debug`, `/query`, `/exec` with no authentication/authorization; endpoints that run client-supplied SQL/commands;
  - **any write route (POST/PUT/PATCH/DELETE) with no authentication** — build a route table (method, path, auth required?, owner/role check?) and flag every write row without auth, except explicit public ones (`/login`, self-signup that cannot set `role`/`active`);
  - **credential/privilege mutation without auth** — an update route that accepts `password`, `email`, `role`, `active`, `is_admin` for the user identified only by the URL id (account takeover, e.g. changing the seeded admin's password);
  - **no ownership check (IDOR)** — a route that receives `/<id>` of a user-owned resource (user, task, order, ...) and updates/deletes it without comparing the owner with the authenticated principal, or accepts an owner field (`user_id`) from the body for someone else;
  - a client-controlled `role`/privilege field accepted on create/update without an admin check.
- **Impact**: full takeover by any anonymous caller (privilege escalation, password reset of any account, data destruction), or by any authenticated user over other users' data.
- **Fix**: playbook P8 (A: remove/guard dangerous endpoints; B: authentication on every write route; C: owner-or-admin checks).
- **Report rule**: the finding's `Recommendation` must enumerate **every** unprotected write route and the rule that applies to each (auth only / owner-or-admin / admin only), because Phase 3 has to implement the whole recommendation.

### AP-05 Broken password storage / homemade crypto
- **Signals**: passwords stored/compared in plaintext (`senha = '...'` compared in SQL); fast unsalted hashes (`md5`, `sha1`, `sha256` alone) for passwords; custom "hash" functions (base64 loops, XOR); default fallback password (`pwd or "123456"`); fake tokens (`'fake-jwt-token-' + id`).
- **Impact**: credential theft, trivial account takeover.
- **Fix**: playbook P6.

---

## HIGH

### AP-06 Business logic in controllers/routes (fat controller)
- **Signals**: route handlers > ~40 lines; handlers that compute totals/discounts/overdue/statistics, run multi-step workflows, or build response objects field by field; model-layer rules (status transitions, stock checks) implemented in the HTTP layer; same handler validates, queries and formats.
- **Impact**: logic not reusable or testable without HTTP.
- **Fix**: playbook P4.

### AP-07 Mutable global state / hidden singletons
- **Signals**: module-level mutable variables (`db_connection = None` + `global`; `globalCache = {}`; `totalRevenue = 0` exported and imported by value); connection shared across requests/threads (`check_same_thread=False`); state in module scope used as cache/service.
- **Impact**: race conditions, hidden coupling, impossible to test, stale copies (exporting a primitive by value never updates).
- **Fix**: playbook P5.

### AP-08 Sensitive data exposure
- **Signals**: responses that include `password`/`senha`/hash/`secret`/`debug`/`db_path`; `to_dict()` serializing credential fields; logs printing card numbers, tokens, keys, passwords; verbose `str(exception)` returned to clients.
- **Impact**: data breach through normal API usage.
- **Fix**: playbook P14.

### AP-09 Tight coupling / no dependency injection
- **Signals**: controllers importing the DB module or opening connections; models instantiating collaborators (`NotificationService()` inside a route, `new sqlite3.Database()` in a constructor); routes importing models directly and calling ORM; services with hardcoded config; circular imports.
- **Impact**: layers cannot be replaced or mocked; violates Dependency Inversion.
- **Fix**: playbook P5 (+ P3/P4).

### AP-10 Missing transactions / data-integrity gaps
- **Signals**: multi-step writes (order + items + stock decrement; enrollment + payment) without a transaction or rollback; deleting a parent without handling children (orphans, "ficaram sujos no banco"); check-then-act stock validation outside the transaction; ignored `err` in write callbacks.
- **Impact**: partial writes, orphaned rows, inconsistent stock/payments.
- **Fix**: playbook P15.

### AP-11 Insecure runtime configuration
- **Signals**: `debug=True`/`DEBUG = True` in the entry point; `host="0.0.0.0"` combined with debug; permissive `CORS(app)` for everything; "ambiente: producao" hardcoded next to debug flag.
- **Impact**: remote code execution via debugger, information leaks.
- **Fix**: playbook P1.

---

## MEDIUM

### AP-12 N+1 queries
- **Signals**: a query executed inside a loop over the rows of another query (`for row in rows: cursor.execute("... WHERE id = " + row[...])`); ORM lazy-loaded relation accessed per item (`len(u.tasks)`, `Model.query.get(t.user_id)` inside `for t in tasks`); callbacks nested per row.
- **Impact**: latency grows linearly with data size.
- **Fix**: playbook P9.

### AP-13 Duplicated code
- **Signals**: the same block (validation, serialization, overdue/status logic, discount tiers) copy-pasted in ≥ 2 places; helper modules that duplicate logic already inlined in routes (or the reverse); two list-to-dict mappers with identical fields.
- **Fix**: playbook P10.

### AP-14 Missing or inconsistent input validation
- **Signals**: `request.get_json()` / `req.body` used without null/type checks; arithmetic/comparison on unvalidated values (`preco < 0` on a string → 500); `int(request.args[...])` without try; required fields checked in create but not in update; validation duplicated with different rules between create/update.
- **Fix**: playbook P4 + P10.

### AP-15 Ad-hoc / inconsistent error handling
- **Signals**: `try/except` wrapped around every handler returning `str(e)`; bare `except:`/`catch (e) {}`; swallowed errors (`catch` with no handling, callbacks that ignore `err`); different error JSON shapes in different handlers; plain-text errors mixed with JSON.
- **Fix**: playbook P7.

### AP-16 Callback hell / unmanaged async flow
- **Signals**: > 3 levels of nested callbacks; manual completion counters (`pending--`, `if (pending === 0) res.json(...)`); results pushed in completion order (non-deterministic output).
- **Fix**: playbook P11.

### AP-17 Deprecated / obsolete API usage
- **Signals** (check the table below for the detected stack; always recommend the modern equivalent).
- **Fix**: playbook P12.

| Stack | Deprecated / obsolete | Modern equivalent |
|---|---|---|
| Python | `datetime.utcnow()` / `utcfromtimestamp()` (deprecated 3.12) | `datetime.now(timezone.utc)` |
| SQLAlchemy ≥ 1.4/2.0 | `Model.query.get(id)` (legacy `Query.get`) | `db.session.get(Model, id)` |
| SQLAlchemy | `Model.query.<...>` legacy query interface in new code | `db.session.execute(db.select(...))` |
| Flask | `@app.before_first_request`, `flask.json.JSONEncoder`, `app.run(debug=True)` as config | app factory / `with app.app_context()`, `app.json` provider, `FLASK_DEBUG` env |
| Python | `hashlib.md5` for passwords, `optparse`, `imp`, `distutils`, `os.popen` | `werkzeug.security` / `hashlib.scrypt`, `argparse`, `importlib`, `subprocess` |
| Python | `print` for diagnostics | `logging` |
| Node | `new Buffer()` / `Buffer()` | `Buffer.from()` / `Buffer.alloc()` |
| Node | `var`, callback style `fs.exists`, `url.parse`, `crypto.createCipher`, `request` pkg, `body-parser` as separate dep with Express ≥ 4.16 | `const/let`, `fs.promises`, `new URL()`, `crypto.createCipheriv`, `fetch`/`axios`, `express.json()` |
| Node | `sqlite3` callback API consumed raw | promisified wrapper / `async-await` |
| Java | `new Date()` / `Calendar`, field `@Autowired`, `WebMvcConfigurerAdapter` | `java.time`, constructor injection, `WebMvcConfigurer` |
| PHP | `mysql_*`, `ereg*` | PDO prepared statements, `preg_*` |
| Go | `ioutil.*` (deprecated 1.16) | `os` / `io` |

---

## LOW

### AP-18 Magic numbers / strings
- **Signals**: unexplained literals in logic (`> 10000`, `* 0.1`, `[1, 5]`, `"pendente"`, `'done'`, `10000` loop count); status/role lists repeated inline; constants defined in a helper but never used.
- **Fix**: playbook P13.

### AP-19 Poor naming
- **Signals**: single-letter or cryptic variables (`u`, `e`, `p`, `cid`, `cc`, `req.body.usr/eml/pwd/c_id` internal names); misleading names (`AppManager` doing everything, `utils` holding config); mixed languages for the same concept.
- **Fix**: rename internally; keep external field names (API contract) intact.

### AP-20 Logging via print/console
- **Signals**: `print(` / `console.log(` for operational logs; "notification" simulated with prints (`ENVIANDO EMAIL...`); noisy logs inside handlers.
- **Fix**: logger (`logging`, `winston`/`console` wrapper) with levels; notifications behind a service.

### AP-21 Dead code / unused imports
- **Signals**: imports never referenced (`json`, `os`, `sys`, `hashlib`, `smtplib`); helper functions with no callers (`process_task_data`, `generate_id`, `log_action`); services instantiated nowhere; exported values never read (`globalCache`, `totalRevenue`).
- **Fix**: delete; if intentionally kept, wire it in.

---

## Detection checklist (quick triage commands, adapt to the stack)

```
# secrets
grep -nEi "(secret|password|passwd|pwd|api[_-]?key|token)\s*[:=]\s*['\"]" <src>
# injection
grep -nE "execute\(.*(\+|%|f\"|format)|\.(run|get|all|query)\(\s*[\`'\"].*(\\$\{|\+)" <src>
# debug
grep -nE "debug\s*=\s*True|DEBUG\s*=\s*True" <src>
# globals
grep -nE "^\s*global |^let [a-zA-Z]+ = (\{\}|\[\]|0)" <src>
# deprecated
grep -nE "utcnow\(|\.query\.get\(|new Buffer|md5" <src>
# bare except / swallowed errors
grep -nE "except:|catch\s*\(\w*\)\s*\{\s*\}" <src>
# logging
grep -nE "print\(|console\.log" <src>
```
