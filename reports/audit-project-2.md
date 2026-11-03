================================
PHASE 1: PROJECT ANALYSIS
================================
Language:      JavaScript (Node.js, sem versão pinada; testado com v24)
Framework:     Express 4.18.2 (^4.18.2)
Dependencies:  express ^4.18.2, sqlite3 ^5.1.6
Domain:        LMS API (cursos, matrículas, pagamentos) com fluxo de checkout e relatório financeiro
Architecture:  Monolítica — `AppManager` (God Class) cria o banco, define schema/seed, registra todas as rotas e executa regras de negócio e SQL dentro dos handlers; `utils.js` mistura configuração, cache global e "criptografia"
Source files:  3 files analyzed (~180 lines)
DB tables:     users, courses, enrollments, payments, audit_logs (SQLite em memória)
Entry point:   src/app.js — `npm start` (porta 3000)
Endpoints:     3 (POST /api/checkout, GET /api/admin/financial-report, DELETE /api/users/:id)
================================

================================
ARCHITECTURE AUDIT REPORT
================================
Project: ecommerce-api-legacy
Stack:   JavaScript (Node.js) + Express 4.18
Files:   3 analyzed | ~180 lines of code

## Summary
CRITICAL: 4 | HIGH: 5 | MEDIUM: 4 | LOW: 4

Deprecated APIs: none detected (o driver `sqlite3` é usado em estilo callback cru — tratado em AP-16)

## Findings

### [CRITICAL] AP-01 Hardcoded Credentials
File: src/utils.js:2-5
Description: `config` contém `dbUser: "admin_master"`, `dbPass: "senha_super_secreta_prod_123"`, `paymentGatewayKey: "pk_live_1234567890abcdef"` (chave live de gateway) e `smtpUser` literais no código-fonte.
Impact: Segredos de produção vazam pelo repositório e não podem ser rotacionados por ambiente.
Recommendation: Ler tudo de variáveis de ambiente em `src/config/settings.js`; sem defaults para segredos (P1).

### [CRITICAL] AP-03 God Class / God File (sem separação de camadas)
File: src/AppManager.js:4-141
Description: A classe `AppManager` cria a conexão SQLite (l.7), define schema e seeds (l.10-23), registra as 3 rotas (l.25-138) e implementa dentro dos handlers SQL, regra de pagamento, criação de usuário, matrícula, auditoria e agregação do relatório.
Impact: Impossível testar ou evoluir qualquer parte isoladamente; toda mudança toca o mesmo arquivo.
Recommendation: Separar em `config/`, `database/`, `models/`, `controllers/`, `views/routes.js`, `middlewares/` e `app.js` como composition root (P3).

### [CRITICAL] AP-05 Broken Password Storage / Homemade Crypto
File: src/utils.js:17-23, src/AppManager.js:68, src/AppManager.js:18
Description: `badCrypto` "hasheia" senhas repetindo 10.000 vezes os 2 primeiros caracteres do base64 e cortando em 10 chars (reversível, sem sal, e bloqueia o event loop); quando `pwd` não é enviado o checkout cria o usuário com senha padrão `"123456"`; o seed grava a senha `'123'` em texto puro.
Impact: Qualquer vazamento do banco revela as senhas; contas criadas sem senha ficam com credencial conhecida.
Recommendation: `crypto.scrypt` com sal aleatório, exigir senha para novos usuários e semear apenas hashes (P6).

### [CRITICAL] AP-04 Unprotected Dangerous Endpoints
File: src/AppManager.js:80-128, src/AppManager.js:131-137
Description: `GET /api/admin/financial-report` (receita e alunos por curso) e `DELETE /api/users/:id` (apaga qualquer usuário) não têm nenhuma autenticação/autorização.
Impact: Qualquer cliente lê dados financeiros e apaga contas.
Recommendation: Proteger rotas administrativas com token configurado por ambiente (P8).

### [HIGH] AP-08 Sensitive Data Exposure
File: src/AppManager.js:45
Description: `console.log` imprime o número completo do cartão e a chave do gateway de pagamento a cada checkout.
Impact: Dados de cartão (PCI) e segredos em logs.
Recommendation: Nunca logar cartão/chaves; logar apenas identificadores (P14).

### [HIGH] AP-06 Business Logic in Controllers/Routes
File: src/AppManager.js:28-77, src/AppManager.js:80-128
Description: O handler de checkout decide o pagamento (`cc.startsWith("4")`), cria usuário, matrícula, pagamento e auditoria; o handler do relatório agrega receita por curso — tudo dentro da rota, com SQL.
Impact: Regras não reutilizáveis/testáveis sem HTTP e banco.
Recommendation: Controllers orquestram o fluxo; gateway de pagamento em service; SQL em models (P4, P3).

### [HIGH] AP-07 Global Mutable State
File: src/utils.js:9-15, src/utils.js:25, src/AppManager.js:2, src/AppManager.js:59
Description: `globalCache` e `totalRevenue` são variáveis de módulo mutáveis exportadas; `totalRevenue` é exportado por valor (nunca atualiza) e `logAndCache` grava um cache que ninguém lê.
Impact: Estado oculto compartilhado entre requisições, comportamento enganoso e vazamento de memória.
Recommendation: Remover o cache global/dead state; se necessário, injetar um serviço com dono único (P5).

### [HIGH] AP-09 Tight Coupling / No Dependency Injection
File: src/AppManager.js:7, src/AppManager.js:45-46, src/app.js:8-10
Description: O construtor instancia o banco diretamente, o gateway de pagamento é simulado inline com a chave global e `app.js` precisa conhecer `initDb`/`setupRoutes` da mesma classe.
Impact: Troca de banco/gateway exige editar a classe inteira; sem possibilidade de mock.
Recommendation: Conexão e serviços criados no composition root e injetados em models/controllers (P5).

### [HIGH] AP-10 Missing Transactions / Integrity Gaps
File: src/AppManager.js:49-62, src/AppManager.js:131-137
Description: Checkout insere matrícula, pagamento e auditoria em passos independentes (erro da auditoria é ignorado, l.57); `DELETE /api/users/:id` remove só o usuário e a própria resposta admite que "as matrículas e pagamentos ficaram sujos no banco".
Impact: Registros órfãos e estados parciais (matrícula sem pagamento).
Recommendation: Transações para checkout e remoção em cascata controlada (P15).

### [MEDIUM] AP-12 N+1 Queries
File: src/AppManager.js:80-128
Description: O relatório consulta cursos, depois matrículas por curso, depois usuário e pagamento por matrícula (3 níveis de queries por linha).
Impact: Número de queries cresce com cursos × matrículas.
Recommendation: Uma query com JOIN agrupada em memória (P9, P11).

### [MEDIUM] AP-16 Callback Hell / Unmanaged Async Flow
File: src/AppManager.js:35-76, src/AppManager.js:80-128
Description: Até 6 níveis de callbacks aninhados com contadores manuais (`coursesPending`, `enrPending`); o relatório é montado na ordem de conclusão das queries (saída não determinística — observado: ordem dos cursos varia entre execuções/estado).
Impact: Difícil de ler e propenso a respostas duplicadas/nunca enviadas.
Recommendation: Promisificar o driver e usar `async/await` (P11).

### [MEDIUM] AP-14 Missing / Inconsistent Input Validation
File: src/AppManager.js:29-35, src/AppManager.js:131-133
Description: Apenas presença de `usr/eml/c_id/card` é checada (sem tipo/formato de e-mail/cartão); `pwd` é opcional e substituído por padrão; `:id` do DELETE não é validado; erros de `err` nas consultas do relatório (l.93, 107, 109) nem são verificados.
Impact: Entradas malformadas causam 500/crash e dados inválidos entram no banco.
Recommendation: Validação no controller com 400 explícito (P4).

### [MEDIUM] AP-15 Ad-hoc Error Handling
File: src/AppManager.js:38-41, src/AppManager.js:51-55, src/AppManager.js:57, src/AppManager.js:133-135
Description: Erros respondidos com `res.status(...).send("Erro DB")` em texto puro enquanto sucessos são JSON; callbacks ignoram `err` (auditoria, delete); sem handler central.
Impact: Contrato de erro inconsistente e falhas silenciosas.
Recommendation: Middleware de erro central + handlers async com `next(err)` (P7).

### [LOW] AP-19 Poor Naming
File: src/AppManager.js:29-33, src/AppManager.js:26, src/utils.js:1-25
Description: Variáveis `u`, `e`, `p`, `cid`, `cc`, `self`; módulo `utils.js` guarda configuração, cache e hashing; classe `AppManager` não descreve nada.
Impact: Legibilidade.
Recommendation: Renomear internamente (`name`, `email`, `password`, `courseId`, `cardNumber`), preservando os campos do JSON de entrada (`usr`, `eml`, `pwd`, `c_id`, `card`).

### [LOW] AP-20 Logging via console.log
File: src/AppManager.js:45, src/utils.js:13, src/app.js:13
Description: Diagnósticos por `console.log` sem nível, inclusive o log do cartão (AP-08).
Impact: Sem controle de nível/destino.
Recommendation: Módulo de logger simples com níveis.

### [LOW] AP-21 Dead Code / Unused Exports
File: src/utils.js:10, src/utils.js:25, src/AppManager.js:2, src/utils.js:2-3
Description: `totalRevenue` importado e nunca usado; `dbUser`, `dbPass`, `smtpUser` nunca lidos; tabela `audit_logs` só recebe escrita.
Impact: Ruído e falsa sensação de funcionalidade.
Recommendation: Remover o que não é usado.

### [LOW] AP-18 Magic Numbers / Strings
File: src/utils.js:19-21, src/AppManager.js:46, src/AppManager.js:68
Description: `10000`, `substring(0, 2)`, `substring(0, 10)`, prefixo de cartão `"4"`, strings `"PAID"`/`"DENIED"` e senha `"123456"` inline.
Impact: Regras de negócio escondidas em literais.
Recommendation: Constantes nomeadas em `config` / service de pagamento (P13).

================================
Total: 17 findings
================================

Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
