================================
PHASE 1: PROJECT ANALYSIS
================================
Language:      Python 3 (sem versão pinada; testado com 3.9)
Framework:     Flask 3.0.0 (+ Flask-SQLAlchemy 3.1.1, Flask-CORS 4.0.0)
Dependencies:  flask, flask-sqlalchemy, flask-cors, marshmallow (não utilizado), requests (não utilizado), python-dotenv (não utilizado)
Domain:        Task Manager API (tasks, usuários, categorias, relatórios, login)
Architecture:  Em camadas "só nas pastas" (models/ routes/ services/ utils/): as rotas concentram validação, regras de negócio, consultas ORM, commit e serialização; não existe camada de controllers; services/ e utils/ têm código morto/duplicado
Source files:  15 files analyzed (~1160 lines)
DB tables:     users, categories, tasks (SQLite via SQLAlchemy, instance/tasks.db)
Entry point:   app.py — `python seed.py` depois `python app.py` (porta 5000)
Endpoints:     22 (GET /, GET /health, GET/POST /tasks, GET /tasks/search, GET /tasks/stats, GET/PUT/DELETE /tasks/<id>, GET/POST /users, GET/PUT/DELETE /users/<id>, GET /users/<id>/tasks, POST /login, GET /reports/summary, GET /reports/user/<id>, GET/POST /categories, PUT/DELETE /categories/<id>)
================================

================================
ARCHITECTURE AUDIT REPORT
================================
Project: task-manager-api
Stack:   Python + Flask 3.0.0 + Flask-SQLAlchemy 3.1.1
Files:   15 analyzed | ~1160 lines of code

## Summary
CRITICAL: 3 | HIGH: 5 | MEDIUM: 5 | LOW: 4

## Findings

### [CRITICAL] AP-01 Hardcoded Credentials
File: app.py:13, services/notification_service.py:7-10
Description: `SECRET_KEY = 'super-secret-key-123'` fixa no código e credenciais SMTP (`taskmanager@gmail.com` / `'senha123'`) hardcoded em `NotificationService.__init__`.
Impact: Segredos versionados no repositório; impossível rotacionar por ambiente.
Recommendation: Ler de variáveis de ambiente em `config/settings.py` (P1).

### [CRITICAL] AP-05 Broken Password Storage / Fake Auth Token
File: models/user.py:27-32, routes/user_routes.py:207-211
Description: Senhas guardadas com `hashlib.md5` sem sal (rápido e quebrável por rainbow table); o login devolve o "token" `'fake-jwt-token-' + str(user.id)`, previsível e sem assinatura.
Impact: Vazamento do banco expõe senhas rapidamente; qualquer um forja o token de qualquer usuário.
Recommendation: `werkzeug.security` (hash salgado e lento) e token assinado com expiração via `itsdangerous` (P6).

### [CRITICAL] AP-04 Unprotected Dangerous Endpoints
File: routes/user_routes.py:43-91, routes/user_routes.py:93-132, routes/user_routes.py:135-151, routes/task_routes.py:226-238, routes/report_routes.py:212-224
Description: Nenhum endpoint exige autenticação: qualquer cliente cria usuário com `role: "admin"` (l.52, 71-78), altera `role`/`active` de qualquer usuário (l.119-125), deleta usuários (com todas as suas tasks), tasks e categorias.
Impact: Escalada de privilégio trivial e destruição de dados por qualquer chamador anônimo.
Recommendation: Exigir token autenticado nas rotas de escrita/administrativas e restringir `role` a administradores (P8).

### [HIGH] AP-08 Sensitive Data Exposure
File: models/user.py:16-25, routes/user_routes.py:28-40, routes/user_routes.py:85-86, routes/user_routes.py:129, routes/user_routes.py:207-210
Description: `User.to_dict()` inclui `password` (hash) e é devolvido por `GET /users/<id>`, `POST /users`, `PUT /users/<id>` e `POST /login`.
Impact: Hashes de senha vazam pelo uso normal da API (e, com MD5, são quebráveis).
Recommendation: Remover `password` da serialização pública (P14).

### [HIGH] AP-06 Business Logic in Controllers/Routes
File: routes/task_routes.py:12-63, routes/task_routes.py:86-154, routes/task_routes.py:157-222, routes/task_routes.py:274-299, routes/user_routes.py:43-91, routes/report_routes.py:13-101
Description: Rotas fazem validação, consultas ORM, regras (overdue, estatísticas, produtividade por usuário), commit e montagem do JSON campo a campo; não existe camada de controllers e as regras que existem nos models (`Task.is_overdue`, `validate_status`) não são usadas.
Impact: Lógica não testável sem HTTP; regras divergem entre rotas.
Recommendation: Criar `controllers/` com o fluxo/validação e mover regras de domínio para os models; rotas ficam finas (P4).

### [HIGH] AP-09 Tight Coupling / No Dependency Injection
File: routes/task_routes.py:2-5, routes/user_routes.py:2-4, routes/report_routes.py:2-5, services/notification_service.py:4-11
Description: Rotas importam `db` e todos os models e executam `Query`/`commit` diretamente; `NotificationService` define host/credenciais SMTP no construtor, imprime em vez de logar e nunca é usado por nenhuma rota.
Impact: Camadas não substituíveis nem mockáveis; serviço órfão.
Recommendation: Rotas → controllers → models; serviço configurado por `config` e injetado/importado pelo controller (P5, P4).

### [HIGH] AP-10 Missing Transactions / Integrity Gaps
File: routes/report_routes.py:212-224, routes/user_routes.py:135-151, routes/task_routes.py:86-154
Description: Excluir categoria deixa `tasks.category_id` apontando para um registro inexistente; excluir usuário apaga tasks em loop manual sem tratar relações; `user_id`/`category_id` do payload não são validados como inteiros antes do uso.
Impact: Referências órfãs e dados inconsistentes.
Recommendation: Anular/validar referências no model/controller dentro de uma transação (P15).

### [HIGH] AP-11 Insecure Runtime Configuration
File: app.py:34, app.py:13-15, app.py:30-31
Description: `app.run(debug=True, host='0.0.0.0', port=5000)` fixo no código, `CORS(app)` totalmente aberto e `db.create_all()` executado na importação do módulo.
Impact: Debugger interativo exposto na rede; efeitos colaterais ao importar `app`.
Recommendation: Config por ambiente, `create_app()` factory, debug desligado por padrão (P1, P5).

### [MEDIUM] AP-12 N+1 Queries
File: routes/task_routes.py:41-58, routes/user_routes.py:22, routes/report_routes.py:53-65, routes/report_routes.py:163, routes/report_routes.py:19-28
Description: `GET /tasks` faz `User.query.get` e `Category.query.get` por task; `GET /users` acessa `len(u.tasks)` (lazy load) por usuário; o resumo executa uma query por usuário, `GET /categories` um `count()` por categoria e 10 `count()` separados em vez de `GROUP BY`.
Impact: Número de queries cresce linearmente com os dados.
Recommendation: Eager loading (`joinedload`) e agregações com `GROUP BY` (P9).

### [MEDIUM] AP-13 Duplicated Code
File: routes/task_routes.py:30-39, routes/task_routes.py:71-80, routes/task_routes.py:284-286, routes/user_routes.py:171-180, routes/report_routes.py:34-43, routes/report_routes.py:132-135
Description: A regra "atrasada" é copiada em 6 lugares apesar de existir `Task.is_overdue` (models/task.py:50-60); a serialização de task aparece em `get_tasks`, `get_user_tasks` e `Task.to_dict`; validação de status/prioridade e regex de e-mail existem em rotas, models e `utils/helpers.py` (l.19-23, 57-107, 110-116).
Impact: Correção em um ponto não chega aos demais.
Recommendation: Uma única implementação no model e validadores compartilhados (P10).

### [MEDIUM] AP-14 Missing / Inconsistent Input Validation
File: routes/task_routes.py:101-115, routes/task_routes.py:175-180, routes/task_routes.py:261-264, routes/report_routes.py:196-202, routes/user_routes.py:100-101, routes/user_routes.py:124-125
Description: `priority < 1` em valor não numérico gera `TypeError` (500); `int(priority)`/`int(user_id)` da busca estouram 500 com texto; `update_category` faz `'name' in data` sem checar `None`; `name` e `active` de usuário não são validados; `POST /categories` não valida cor.
Impact: 500 em entradas inválidas e regras diferentes entre create/update.
Recommendation: Validadores únicos retornando 400 (P4, P10).

### [MEDIUM] AP-15 Ad-hoc Error Handling
File: routes/task_routes.py:62, routes/task_routes.py:137, routes/task_routes.py:204, routes/task_routes.py:236, routes/user_routes.py:130, routes/user_routes.py:149, routes/report_routes.py:186, routes/report_routes.py:207, routes/report_routes.py:221
Description: `except:` genérico engole qualquer exceção (inclui `KeyboardInterrupt`), respostas de erro montadas rota a rota e alguns erros apenas via `print`.
Impact: Falhas reais mascaradas como "Erro interno".
Recommendation: Handler central + exceções de domínio (P7).

### [MEDIUM] AP-17 Deprecated API Usage
File: models/task.py:15-16, models/task.py:52, routes/task_routes.py:42, routes/task_routes.py:67, routes/user_routes.py:29, routes/report_routes.py:105, routes/report_routes.py:35, services/notification_service.py:35
Description: `datetime.utcnow()` (deprecated no Python 3.12) em ~20 pontos e `Model.query.get()` (API legada do SQLAlchemy 2.0) em ~17 pontos (`task_routes.py:42,51,67,117,122,158,188,195,227`, `user_routes.py:29,94,136,155`, `report_routes.py:105,192,213`).
Impact: `DeprecationWarning`/`LegacyAPIWarning` hoje, quebra em versões futuras.
Recommendation: `datetime.now(timezone.utc)` via helper `utcnow()` e `db.session.get(Model, id)` (P12).

### [LOW] AP-21 Dead Code / Unused Imports
File: app.py:7, routes/task_routes.py:7, routes/user_routes.py:6, routes/report_routes.py:7-8, models/task.py:3, utils/helpers.py:1-7, utils/helpers.py:25-40, utils/helpers.py:52-107
Description: `os, sys, json, time, hashlib, format_date, calculate_percentage` importados e não usados; helpers sem nenhum chamador (`sanitize_string`, `generate_id`, `log_action`, `is_valid_color`, `process_task_data`); constantes de `helpers.py:110-116` nunca usadas; `marshmallow`, `requests` e `python-dotenv` no requirements sem uso.
Impact: Ruído e falsa sensação de reaproveitamento.
Recommendation: Remover o que não é usado e ligar o que deveria ser (constantes em `config`).

### [LOW] AP-18 Magic Numbers / Strings
File: routes/task_routes.py:106-112, routes/user_routes.py:64-71, routes/user_routes.py:115-120, routes/report_routes.py:45
Description: Listas de status/roles, faixa de prioridade `1..5`, tamanhos `3`/`200`/`4`, janela de `7` dias e prioridades `p1..p5` inline.
Impact: Regras escondidas em literais e repetidas.
Recommendation: Constantes nomeadas em `config/settings.py` (P13).

### [LOW] AP-20 Logging via print
File: routes/task_routes.py:149, routes/task_routes.py:153, routes/task_routes.py:219, routes/task_routes.py:234, routes/user_routes.py:83, routes/user_routes.py:89, routes/user_routes.py:147, services/notification_service.py:21, services/notification_service.py:24, utils/helpers.py:39-41
Description: Diagnósticos por `print`.
Impact: Sem níveis nem destino configurável.
Recommendation: `logging` (P12).

### [LOW] AP-19 Poor Naming / Misplaced Responsibility
File: routes/report_routes.py:157-224, routes/report_routes.py:24-28
Description: O CRUD de categorias vive em `report_routes.py`; variáveis `p1..p5`, `t`, `u`, `cat`.
Impact: Difícil de localizar código por domínio.
Recommendation: `category_routes.py`/`category_controller.py` próprios; nomes descritivos.

================================
Total: 17 findings
================================

Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
