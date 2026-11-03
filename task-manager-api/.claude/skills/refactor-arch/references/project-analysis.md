# Project Analysis Heuristics (Phase 1)

Goal: identify the stack and the current architecture **from evidence in the repository**, never from assumptions. Use manifests first, then imports, then file layout.

## 1. Inventory

- Ignore: `.git`, `node_modules`, `.venv`, `venv`, `__pycache__`, `dist`, `build`, `target`, `bin`, `obj`, `.claude`, `.idea`, `.vscode`, lock files, `*.db`/`*.sqlite`, images, and generated files.
- Count only source files (`.py .js .ts .java .go .php .rb .cs .kt`…) and approximate lines with `wc -l`.
- Read README/Makefile/Dockerfile/`package.json` scripts for the official boot command.

## 2. Language detection

| Evidence | Language |
|---|---|
| `requirements.txt`, `pyproject.toml`, `Pipfile`, `setup.py`, `*.py` | Python |
| `package.json`, `*.js`, `*.mjs`, `*.cjs` | JavaScript (Node.js) |
| `tsconfig.json`, `*.ts` | TypeScript |
| `pom.xml`, `build.gradle(.kts)`, `*.java`, `*.kt` | Java / Kotlin |
| `go.mod`, `*.go` | Go |
| `composer.json`, `*.php` | PHP |
| `Gemfile`, `*.rb` | Ruby |
| `*.csproj`, `*.sln`, `*.cs` | C# / .NET |

Runtime version: look at `engines` in `package.json`, `python_requires`, `.python-version`, `go.mod` `go` directive, `<java.version>` in pom, or run `--version` if available.

## 3. Framework detection (manifest dependency + code signature)

| Language | Dependency | Code signature | Framework |
|---|---|---|---|
| Python | `flask` | `Flask(__name__)`, `@app.route`, `add_url_rule`, `Blueprint` | Flask |
| Python | `fastapi` | `FastAPI()`, `@app.get` | FastAPI |
| Python | `django` | `manage.py`, `urls.py`, `settings.py` | Django |
| Node | `express` | `express()`, `app.get/post`, `Router()` | Express |
| Node | `@nestjs/core` | `@Controller`, `@Injectable` | NestJS |
| Node | `fastify`, `koa`, `hapi` | respective factory calls | Fastify/Koa/Hapi |
| Java | `spring-boot-starter-web` | `@RestController`, `@SpringBootApplication` | Spring Boot |
| Go | `gin-gonic/gin`, `go-chi/chi`, `labstack/echo`, stdlib `net/http` | `gin.Default()`, `http.HandleFunc` | Gin/Chi/Echo/net-http |
| PHP | `laravel/framework`, `symfony/*` | `routes/web.php`, `artisan` | Laravel/Symfony |
| Ruby | `rails`, `sinatra` | `config/routes.rb` | Rails/Sinatra |
| C# | `Microsoft.AspNetCore` | `[ApiController]`, `MapGet` | ASP.NET Core |

Record the **version** from the manifest (pin or range). Record notable extras: CORS, ORM, validation libs, auth libs, HTTP client, env loaders.

## 4. Database / persistence detection

| Signal | Conclusion |
|---|---|
| `sqlite3`, `sqlite:///`, `:memory:`, `*.db` | SQLite (note file vs in-memory) |
| `psycopg2`, `pg`, `postgres://` | PostgreSQL |
| `mysql`, `mysql2`, `PyMySQL` | MySQL/MariaDB |
| `pymongo`, `mongoose` | MongoDB |
| `redis` | Redis |
| `SQLAlchemy`, `flask_sqlalchemy`, `db.Model`, Sequelize, TypeORM, Prisma, Hibernate/JPA, GORM, ActiveRecord | ORM in use |
| `cursor.execute`, `db.run/get/all`, `query(` with string SQL | Raw SQL |

Also extract: **tables/models and relations** (`CREATE TABLE`, model classes), **how connections are opened** (module-level global? per request? pool?), **where schema/seed is created**.

## 5. Domain detection

Infer from route names, table/model names, constants and seed data. State it in one line (e.g. "E-commerce API (products, orders, users)", "LMS API with checkout flow", "Task Manager API"). Mention the main flows (checkout, order creation, reports).

## 6. Architecture mapping

For every source file, determine which responsibilities it mixes:

| Responsibility | Typical signals |
|---|---|
| Routing / transport | route decorators, `app.get`, `add_url_rule`, `Blueprint`, request parsing, `jsonify`, `res.json` |
| Controller / flow | orchestration of validation + model calls + response |
| Business rules | pricing, discounts, state transitions, stock rules, overdue rules |
| Data access | SQL strings, ORM queries, connection management, schema/seed |
| Configuration | secrets, ports, flags, env reads |
| Cross-cutting | logging, error handling, auth, notifications, caching |
| Integrations | payment gateway, SMTP, HTTP clients |

Then classify the current architecture, in one sentence:

- **Monolithic / flat**: few files, several responsibilities per file (e.g. one file with routes + SQL + business logic).
- **Layered but leaky**: layers exist by folder (`models/`, `routes/`, `services/`, `utils/`) but routes contain business logic/queries, models contain presentation concerns, helpers are unused/duplicated.
- **Already MVC-like**: say what is missing against `mvc-guidelines.md`.

Note explicitly: god files (> ~250 lines or > 3 responsibilities), global mutable state, composition root location, whether there is any test suite.

## 7. Endpoint inventory

Extract every endpoint: method, path, handler, whether it touches the DB, auth requirements (usually none). This list drives Phase 3 validation. Include health/admin/debug endpoints.
