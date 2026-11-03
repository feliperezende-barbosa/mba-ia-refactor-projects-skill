# MVC Architecture Guidelines (Phase 3 target)

Target pattern for **API backends** (JSON, no server-rendered HTML): the "View" is the **routing/presentation layer** that maps HTTP to controllers and shapes the HTTP response.

## Layers and responsibilities

| Layer | Owns | Must NOT |
|---|---|---|
| **Config** (`config/`) | Reads env vars, defaults for non-secret values, constants (ports, limits, valid statuses, tiers). Single source of truth. | Contain secrets in source. Import other layers. |
| **Models** (`models/`) | Data structures + **all data access** (SQL/ORM), schema, seeds, entity invariants (e.g. `is_overdue`, `serialize()` without sensitive fields). Return plain data/entities. | Import the web framework (`request`, `jsonify`, `res`). Format HTTP responses. Know about routes. |
| **Views / Routes** (`views/` or `routes/`) | Map URL + HTTP verb → controller function; register blueprints/routers. Nothing else. | Contain business rules, SQL, validation logic beyond routing params. |
| **Controllers** (`controllers/`) | Application flow: read request → validate → call models/services → build response/status. Own business rules that orchestrate several models (order creation, checkout, report aggregation). | Contain SQL or connection handling. Be imported by models. |
| **Services** (`services/`, optional) | Integrations and cross-cutting capabilities: notifications/e-mail, payment gateway, password hashing, token signing. Injected/imported by controllers. | Touch HTTP objects. Hold hidden global state. |
| **Middlewares** (`middlewares/`) | Cross-cutting HTTP concerns: central error handler, (optional) auth, request logging. | Contain business logic. |
| **Composition root** (`app.py` / `app.js` / `main.go`) | Build the app: load config, init DB, register routes + error handlers, start server. Small (< ~50 lines). | Contain routes with logic or SQL. |

## Dependency rule

```
routes/views ──► controllers ──► models ──► database
                     │
                     └──► services

config ◄── (everyone may read)        middlewares ◄── registered by composition root
```

- Dependencies point **inward/down only**. Models never import controllers/routes. Controllers never import routes.
- Dependencies are **passed in or resolved at the composition root**, not created inside handlers (no `new Service()` per request, no module-level mutable connection). Per-request DB access: framework request context (`flask.g`), a pool, or an injected repository.
- Models receive the DB handle (or fetch it from a connection module); they never create global singletons.

## Cross-cutting rules

1. **Configuration**: everything environment-specific (secrets, DB path/URL, ports, debug flag, SMTP, payment keys) comes from env vars with safe defaults (`DEBUG=false`). Provide `.env.example`. Secrets have no committed default; generate a random one at boot for dev if not set.
2. **Error handling**: controllers raise/return domain errors (e.g. `ValidationError`, `NotFoundError`) → **one** error handler maps them to the HTTP status + the *original* JSON error shape. Unknown exceptions → log with stack trace, return a generic 500 without internals.
3. **Validation**: at the controller boundary, one helper per entity (shared by create/update); return 400 with the same message style as the original.
4. **Serialization**: one place per entity (`to_dict`/`serialize`) — never expose password/hash/secret fields.
5. **Transactions**: multi-step writes in one transaction at the model/controller boundary.
6. **Logging**: use the language logger; no `print`/`console.log` in layers.
7. **Entry point**: keep the original boot command working (`python app.py`, `npm start`).
8. **Naming**: keep the project's existing language for domain terms (e.g. `produtos`, `pedidos`) and its framework conventions; do not rename public routes or JSON fields.

## Target layouts

Adapt names to the project; always include every layer.

### Python / Flask (flat project)
```
project/
├── app.py                      # composition root: create_app(), run
├── config/settings.py          # env-driven config + constants
├── database/connection.py      # connection per request (flask.g), schema init, seed
├── models/<entity>_model.py    # data access + serialization
├── services/<capability>.py    # notifications, password hashing…
├── controllers/<entity>_controller.py
├── views/routes.py             # Blueprint: URL → controller
├── middlewares/error_handler.py
└── utils/validators.py         # (optional) shared validation helpers
```

### Python / Flask (already layered: models/ routes/ services/ utils/)
Keep existing folders and conventions, but:
- Add `controllers/` and move the logic out of `routes/` (routes become thin).
- Move helpers actually used into `utils/`, delete the unused ones, move constants to `config/`.
- Use an app factory (`create_app`) in `app.py`; config in `config/settings.py`; central handler in `middlewares/error_handler.py`.
- Move computed domain rules (overdue, validation lists) onto the models / config.

### Node.js / Express
```
project/
├── src/
│   ├── app.js                  # composition root: createApp(), listen
│   ├── config/settings.js      # env-driven config
│   ├── database/connection.js  # opens DB, promisified helpers, schema + seed
│   ├── models/<entity>Model.js # data access only
│   ├── services/               # paymentGateway, password hashing…
│   ├── controllers/<x>Controller.js
│   ├── views/routes.js         # express.Router(): URL → controller
│   └── middlewares/errorHandler.js
└── package.json
```

### Other stacks (same layering, idiomatic names)
- **Spring Boot**: `config/`, `repository/` (models/data), `model|entity/`, `service/`, `controller/` (+ `@RestControllerAdvice` for errors).
- **Go**: `internal/config`, `internal/model`, `internal/repository`, `internal/handler` (views/controllers), `internal/middleware`, `cmd/<app>/main.go`.
- **Django/DRF**: `models.py`, `views.py` (controllers), `urls.py` (routes), `services.py`, middleware.
- **Laravel**: `app/Models`, `app/Http/Controllers`, `routes/api.php`, `app/Services`, `app/Exceptions/Handler`.

## Acceptance checklist for the refactored project

- [ ] Config module, no hardcoded secrets/ports in code
- [ ] Models abstract all data access (zero SQL/ORM outside models/database)
- [ ] Routes only map URL → controller
- [ ] Controllers hold the flow/business rules (no SQL, no connection handling)
- [ ] Central error handler; no `str(e)` leaked to clients
- [ ] Clear entry point / composition root
- [ ] No global mutable state; no string-built SQL; no deprecated APIs from the catalog
- [ ] Application boots; all original endpoints respond
