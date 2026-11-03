================================
PHASE 1: PROJECT ANALYSIS
================================
Language:      Python 3 (no version pinned)
Framework:     Flask 3.1.1
Dependencies:  flask==3.1.1, flask-cors==5.0.1 (stdlib sqlite3 for persistence)
Domain:        E-commerce API (produtos, usuários, pedidos, relatórios de vendas)
Architecture:  Monolítica — 4 arquivos planos (app.py, controllers.py, models.py, database.py); "controllers" e "models" existem só no nome: o models.py concentra SQL + regras de negócio + formatação, o app.py mistura rotas, endpoints admin e acesso direto ao banco
Source files:  4 files analyzed (~780 lines)
DB tables:     produtos, usuarios, pedidos, itens_pedido (SQLite, arquivo loja.db, conexão global)
Entry point:   app.py — `python app.py` (porta 5000)
Endpoints:     19 (GET /, GET /health, GET/POST /produtos, GET /produtos/busca, GET/PUT/DELETE /produtos/<id>, GET/POST /usuarios, GET /usuarios/<id>, POST /login, GET/POST /pedidos, GET /pedidos/usuario/<id>, PUT /pedidos/<id>/status, GET /relatorios/vendas, POST /admin/reset-db, POST /admin/query)
================================

================================
ARCHITECTURE AUDIT REPORT
================================
Project: code-smells-project
Stack:   Python + Flask 3.1.1
Files:   4 analyzed | ~780 lines of code

## Summary
CRITICAL: 5 | HIGH: 6 | MEDIUM: 4 | LOW: 4

Deprecated APIs: none detected (flask 3.1.1 / sqlite3 stdlib usados de forma compatível; ver AP-11 para o uso de `debug=True` como configuração)

## Findings

### [CRITICAL] AP-01 Hardcoded Credentials
File: app.py:7, controllers.py:289
Description: `SECRET_KEY` fixa no código (`"minha-chave-super-secreta-123"`) e a mesma chave é devolvida em texto puro pelo endpoint `/health`.
Impact: Qualquer pessoa com acesso ao repositório (ou a `/health`) conhece a chave de assinatura de sessões; impossível rotacionar por ambiente.
Recommendation: Ler `SECRET_KEY` de variável de ambiente em um módulo `config/settings.py` e nunca expô-la (P1).

### [CRITICAL] AP-02 SQL Injection
File: models.py:28, models.py:48-49, models.py:58-60, models.py:68, models.py:92, models.py:110, models.py:127-128, models.py:140, models.py:149-165, models.py:174, models.py:188, models.py:224, models.py:280, models.py:291-297
Description: Todas as queries são montadas por concatenação de strings com dados da requisição (login, busca de produtos, criação/atualização de produto e usuário, pedidos, status). Confirmado em execução: `POST /login` com `{"email": "' OR '1'='1' --"}` retorna 200 e autentica como Admin.
Impact: Bypass de autenticação, leitura e destruição de qualquer tabela.
Recommendation: Usar queries parametrizadas (`cursor.execute("... WHERE email = ?", (email,))`) em todos os models (P2).

### [CRITICAL] AP-03 God Class / God File (sem separação de camadas)
File: models.py:1-314, controllers.py:1-292, app.py:47-79
Description: `models.py` contém SQL, regras de negócio (cálculo de total, checagem de estoque, faixas de desconto em `relatorio_vendas`), montagem de dicts de resposta e 4 domínios diferentes; `controllers.py` valida, consulta o banco (`health_check`) e formata resposta; `app.py` registra rotas, define endpoints administrativos e executa SQL.
Impact: Impossível testar em isolamento; qualquer mudança afeta todos os domínios.
Recommendation: Separar em `models/` por entidade, `controllers/` por domínio, `views/routes.py`, `config/`, `middlewares/` e um `app.py` apenas como composition root (P3).

### [CRITICAL] AP-04 Unprotected Dangerous Endpoints
File: app.py:47-57, app.py:59-79
Description: `POST /admin/query` executa SQL arbitrário enviado no body e `POST /admin/reset-db` apaga todas as tabelas, ambos sem qualquer autenticação.
Impact: Qualquer cliente da rede pode ler, alterar ou destruir todo o banco.
Recommendation: Remover `/admin/query`; manter `/admin/reset-db` somente atrás de token administrativo configurado por ambiente (P8).

### [CRITICAL] AP-05 Broken Password Storage
File: database.py:73-79, models.py:105-112, models.py:122-130
Description: Senhas são gravadas e comparadas em texto puro (seeds `admin123`, `123456`, `senha123`; `login_usuario` compara `senha` direto no SQL; `criar_usuario` grava a senha recebida sem hash).
Impact: Vazamento do banco expõe todas as credenciais imediatamente.
Recommendation: Armazenar hash salgado (`werkzeug.security.generate_password_hash`) e verificar com `check_password_hash` (P6).

### [HIGH] AP-08 Sensitive Data Exposure
File: models.py:72-87, models.py:89-103, controllers.py:286-289
Description: `GET /usuarios` e `GET /usuarios/<id>` retornam o campo `senha`; `GET /health` retorna `secret_key`, `debug` e `db_path`; logs imprimem e-mails de login (`controllers.py:179,182`).
Impact: Vazamento de credenciais e segredos pelo uso normal da API.
Recommendation: Remover `senha` do serializer de usuário e reduzir `/health` a status/contagens (P14).

### [HIGH] AP-06 Business Logic in Controllers/Models
File: controllers.py:24-62, controllers.py:237-255, models.py:133-168, models.py:235-272
Description: Validação de produto (nome, preço, categorias válidas), transições de status e notificações ficam no controller; cálculo de total/estoque do pedido e a tabela de descontos do relatório ficam misturados ao SQL no model.
Impact: Regras não reutilizáveis nem testáveis sem HTTP/SQL; duplicação entre create e update.
Recommendation: Controllers orquestram e validam (helper único de validação); models só acessam dados; constantes de negócio em `config` (P4, P10, P13).

### [HIGH] AP-07 Global Mutable State
File: database.py:4-10, database.py:86
Description: Conexão SQLite em variável global `db_connection` criada com `check_same_thread=False` e compartilhada por todas as requisições/threads; `db_path` global.
Impact: Condições de corrida, impossibilidade de isolar testes, schema/seed executados como efeito colateral do primeiro `get_db()`.
Recommendation: Conexão por requisição via `flask.g` + inicialização de schema/seed explícita no boot (P5).

### [HIGH] AP-09 Tight Coupling / No Dependency Injection
File: controllers.py:3, controllers.py:264-272, app.py:4, app.py:47-79
Description: `controllers.health_check` e as rotas admin importam `get_db` e executam SQL diretamente; controllers importam `models` como módulo e dependem de estado global.
Impact: Camadas não substituíveis; violação do Dependency Inversion.
Recommendation: Acesso a dados exclusivamente em models; dependências ligadas no composition root (P5, P3).

### [HIGH] AP-10 Missing Transactions / Integrity Gaps
File: models.py:133-168
Description: `criar_pedido` valida estoque, insere pedido, itens e decrementa estoque em passos separados, com `return` antecipado sem rollback e commit único no fim; verificação de estoque e decremento não são atômicos.
Impact: Pedidos parciais e estoque inconsistente sob concorrência ou falha.
Recommendation: Envolver criação de pedido em uma transação com rollback (P15).

### [HIGH] AP-11 Insecure Runtime Configuration
File: app.py:8, app.py:88
Description: `DEBUG = True` e `app.run(host="0.0.0.0", port=5000, debug=True)` fixos no código; `/health` ainda informa `"ambiente": "producao"` com debug ligado.
Impact: Debugger interativo (execução remota de código) exposto em todas as interfaces.
Recommendation: Debug/host/porta vindos de variáveis de ambiente, padrão `debug=False`, `127.0.0.1` (P1).

### [MEDIUM] AP-12 N+1 Queries
File: models.py:171-200, models.py:203-232
Description: Para cada pedido é feita uma query de itens e, para cada item, outra query de produto (`cursor2`, `cursor3`).
Impact: Número de queries cresce com pedidos × itens.
Recommendation: Um único `JOIN` agrupando em memória (P9).

### [MEDIUM] AP-13 Duplicated Code
File: models.py:4-22, models.py:24-40, models.py:285-310, models.py:171-232, controllers.py:24-62, controllers.py:64-96
Description: O mapeamento row→dict de produto aparece 3 vezes e o de usuário 2; `get_pedidos_usuario` e `get_todos_pedidos` são cópias; validação de create/update de produto duplicada e divergente.
Impact: Correções precisam ser replicadas; comportamento inconsistente.
Recommendation: Serializers e validadores únicos (P10).

### [MEDIUM] AP-14 Missing / Inconsistent Input Validation
File: controllers.py:64-96, controllers.py:111-126, controllers.py:167-186, controllers.py:188-220, controllers.py:237-240
Description: Update de produto não valida tamanho do nome nem categoria (create valida); `preco`/`estoque` não têm checagem de tipo (string → `TypeError` → 500); `float(preco_min)` sem tratamento; `login` e `atualizar_status_pedido` usam `dados.get` sem checar `None`; itens do pedido não validam `produto_id`/`quantidade`.
Impact: 500 em entradas inválidas e regras diferentes entre rotas.
Recommendation: Validador compartilhado por entidade retornando 400 (P4, P10).

### [MEDIUM] AP-15 Ad-hoc Error Handling
File: controllers.py:5-292, app.py:77-78
Description: Cada handler tem seu próprio `try/except Exception` que devolve `str(e)` ao cliente e faz `print`; formatos de erro misturam `{"erro"}` e `{"erro","sucesso"}`.
Impact: Vazamento de detalhes internos e tratamento inconsistente.
Recommendation: Handler centralizado (erros de domínio → status; exceções inesperadas → log + 500 genérico) (P7).

### [LOW] AP-18 Magic Numbers / Strings
File: models.py:256-262, controllers.py:52, controllers.py:242
Description: Faixas de desconto (`10000/0.1`, `5000/0.05`, `1000/0.02`), lista de categorias e lista de status inline.
Impact: Regras de negócio escondidas em literais.
Recommendation: Constantes nomeadas em `config/settings.py` (P13).

### [LOW] AP-20 Logging via print
File: controllers.py:8, controllers.py:57, controllers.py:179, controllers.py:208-210, controllers.py:248-250, app.py:56, app.py:83-86
Description: Diagnósticos e "notificações" (EMAIL/SMS/PUSH) simulados com `print`.
Impact: Sem níveis, sem destino configurável; notificações acopladas ao controller.
Recommendation: `logging` + um `notification_service` (P12).

### [LOW] AP-21 Dead Code / Unused Imports
File: database.py:2, models.py:2
Description: `import os` (database.py) e `import sqlite3` (models.py) nunca usados.
Impact: Ruído.
Recommendation: Remover.

### [LOW] AP-19 Poor Naming
File: controllers.py:14, controllers.py:64, models.py:24, models.py:187-191
Description: Parâmetro `id` sombreia o builtin; `cursor2`/`cursor3`.
Impact: Legibilidade.
Recommendation: Renomear (`produto_id`) preservando as rotas.

================================
Total: 19 findings
================================

Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
