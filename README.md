# Criação de Skills — Refatoração Arquitetural Automatizada

Ao longo do curso você aprendeu o que são Skills e como elas permitem que um agente de IA atue como um especialista em tarefas específicas. Agora imagine o seguinte cenário: você herdou 3 projetos legados com problemas de arquitetura, segurança e qualidade de código. Revisar e corrigir tudo manualmente levaria dias.

Neste desafio, você vai criar uma Skill que automatiza esse processo — analisando, auditando e refatorando qualquer projeto para o padrão MVC, independente da tecnologia.

## Objetivo

Você deve entregar uma Skill capaz de:

- Analisar uma codebase detectando linguagem, framework e arquitetura atual
- Identificar anti-patterns e code smells, classificando por severidade com arquivo e linha exatos
- Gerar um relatório de auditoria estruturado com todos os achados
- Refatorar o projeto para o padrão MVC (Model-View-Controller), eliminando os problemas encontrados
- Validar o resultado garantindo que a aplicação continua funcionando após as mudanças

A skill deve ser agnóstica de tecnologia, funcionando com diferentes linguagens e frameworks.

## Contexto

### Definição de Severidades

Para padronizar a sua auditoria e os relatórios gerados pela IA, utilize a seguinte escala de classificação baseada em problemas de MVC e SOLID:

- **CRITICAL:** Falhas graves de arquitetura ou segurança que impedem o funcionamento correto, expõem dados sensíveis (ex: credenciais hardcoded, SQL Injection) ou violam completamente a separação de responsabilidades (ex: "God Class" contendo banco de dados, lógicas complexas e roteamento no mesmo arquivo).
- **HIGH:** Fortes violações do padrão MVC ou princípios SOLID que dificultam muito a manutenção e testes (ex: lógicas de negócio pesadas presas dentro de Controllers, forte acoplamento sem Injeção de Dependência, ou uso de estado global mutável em toda a aplicação).
- **MEDIUM:** Problemas de padronização, duplicação de código ou gargalos de performance moderada (ex: Queries N+1 no banco de dados, uso inadequado de middlewares, validações ausentes nas rotas).
- **LOW:** Melhorias de legibilidade, nomenclatura de variáveis ruins, ou "magic numbers" soltos pelo código.

### Exemplo de Uso no CLI

```bash
# Executar a skill no projeto com problemas
cd code-smells-project
claude "/refactor-arch"
```

```
================================
PHASE 1: PROJECT ANALYSIS
================================
Language:      Python
Framework:      Flask 3.1.1
Dependencies:  flask-cors
Domain:        E-commerce API (produtos, pedidos, usuários)
Architecture:  Monolítica — tudo em 4 arquivos, sem separação de camadas
Source files:  4 files analyzed
DB tables:     produtos, usuarios, pedidos, itens_pedido
================================
```

```
================================
ARCHITECTURE AUDIT REPORT
================================
Project: code-smells-project
Stack:   Python + Flask
Files:   4 analyzed | ~800 lines of code

## Summary
CRITICAL: 4 | HIGH: 5 | MEDIUM: 2 | LOW: 3

## Findings

### [CRITICAL] God Class / God Method
File: models.py:1-350
Description: Arquivo único contém toda lógica de negócio, queries SQL, validação e formatação para 4 domínios diferentes.
Impact: Impossível testar em isolamento, qualquer mudança afeta tudo.
Recommendation: Separar em models e controllers por domínio.

### [CRITICAL] Hardcoded Credentials
File: app.py:8
Description: SECRET_KEY hardcoded como 'minha-chave-super-secreta-123'
...

================================
Total: 14 findings
================================

Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
> y
```

```
[... refatoração executada ...]

================================
PHASE 3: REFACTORING COMPLETE
================================
## New Project Structure
src/
├── config/settings.py
├── models/
│   ├── produto_model.py
│   └── usuario_model.py
├── views/
│   └── routes.py
├── controllers/
│   ├── produto_controller.py
│   └── pedido_controller.py
├── middlewares/error_handler.py
└── app.py (composition root)

## Validation
  ✓ Application boots without errors
  ✓ All endpoints respond correctly
  ✓ Zero anti-patterns remaining
================================
```

## Tecnologias obrigatórias

- **Ferramenta:** uma das três opções abaixo (não são aceitas outras ferramentas):
  - Claude Code
  - Gemini CLI
  - OpenAI Codex
- **Recurso:** Custom Skills (ou o equivalente na ferramenta escolhida)
- **Formato dos arquivos de referência:** Markdown
- **Projetos-alvo:** Python/Flask (2 projetos) e Node.js/Express (1 projeto) (fornecidos no repositório base)

> **Nota sobre a ferramenta:** Os exemplos deste documento usam o Claude Code (`.claude/skills/`) como referência, pois é a ferramenta utilizada no curso. Se você optar por Gemini CLI ou Codex, adapte o nome da pasta e o comando de invocação conforme a convenção dela — o conceito de skill e a estrutura interna (SKILL.md + arquivos de referência) permanecem os mesmos.

## Requisitos

### 1. Análise Manual dos Projetos

Antes de criar a skill, você deve entender os problemas que ela vai resolver.

**Tarefas:**

- Analisar o projeto `code-smells-project/` (Python/Flask — API de E-commerce)
- Analisar o projeto `ecommerce-api-legacy/` (Node.js/Express — LMS API com fluxo de checkout)
- Analisar o projeto `task-manager-api/` (Python/Flask — API de Task Manager)

Para cada projeto, identificar e documentar no mínimo 5 problemas, incluindo pelo menos:

- 1 de severidade CRITICAL ou HIGH
- 2 de severidade MEDIUM
- 2 de severidade LOW

Documentar os achados na seção "Análise Manual" do seu `README.md`

> **Dica:** Não precisa encontrar todos os problemas — foque nos que têm maior impacto arquitetural. Use os projetos como insumo para entender quais padrões sua skill precisa detectar.

> **Por que 3 projetos?** Dois são Python/Flask (com níveis de organização diferentes) e um é Node.js/Express. Sua skill precisa funcionar nos 3 para provar que é verdadeiramente agnóstica de tecnologia — lidando tanto com código completamente desestruturado quanto com projetos que já possuem alguma separação de camadas.

### 2. Criação da Skill

Agora que você conhece os problemas, crie uma skill que os detecte, gere um relatório de auditoria e corrija automaticamente.

**Tarefas:**

Criar a skill dentro do projeto `code-smells-project/` e implementar o SKILL.md com 3 fases sequenciais:

- **Fase 1 — Análise:** Detectar stack, mapear arquitetura atual, imprimir resumo
- **Fase 2 — Auditoria:** Cruzar código contra catálogo de anti-patterns, gerar relatório, pedir confirmação
- **Fase 3 — Refatoração:** Reestruturar para o padrão MVC, validar que funciona

Criar arquivos de referência em Markdown que forneçam à skill o conhecimento necessário para executar as 3 fases. Os arquivos devem cobrir **obrigatoriamente** as seguintes áreas de conhecimento:

| Área de conhecimento | O que deve conter |
|---|---|
| Análise de projeto | Heurísticas para detecção de linguagem, framework, banco de dados e mapeamento de arquitetura |
| Catálogo de anti-patterns | Anti-patterns com sinais de detecção e classificação de severidade |
| Template de relatório | Formato padronizado do relatório de auditoria (Fase 2) |
| Guidelines de arquitetura | Regras do padrão MVC alvo (camadas Models, Views/Routes e Controllers, responsabilidades de cada uma) |
| Playbook de refatoração | Padrões concretos de transformação para cada anti-pattern (com exemplos de código) |

> **Nota:** Você tem liberdade para organizar os arquivos de referência como preferir — pode usar os nomes e a quantidade de arquivos que fizer sentido para sua skill. O importante é que todas as 5 áreas de conhecimento estejam cobertas. O nome da skill (`refactor-arch`) e o arquivo `SKILL.md` são obrigatórios e não devem ser alterados. O path da skill segue a convenção da ferramenta escolhida (no Claude Code, por exemplo, é `.claude/skills/refactor-arch/`).

**Requisitos da skill:**

- Deve ser agnóstica de tecnologia — deve funcionar corretamente nos 3 projetos fornecidos, independente da stack ou nível de organização
- O catálogo de anti-patterns deve conter no mínimo 8 anti-patterns com severidade distribuída (CRITICAL, HIGH, MEDIUM, LOW)
- O catálogo deve incluir detecção de APIs deprecated — identificar uso de APIs obsoletas e recomendar o equivalente moderno
- O playbook deve ter no mínimo 8 padrões de transformação com exemplos de código antes/depois
- A Fase 2 deve pausar e pedir confirmação antes de modificar qualquer arquivo
- A Fase 3 deve validar o resultado (boot da aplicação + endpoints funcionando)

### 3. Execução da Skill

Execute sua skill nos 3 projetos e valide que ela funciona em todas as stacks.

#### Projeto 1 — code-smells-project (Python/Flask)

Invocar a skill no Claude Code:

```bash
claude "/refactor-arch"
```

> **Nota:** O comando acima é o exemplo com Claude Code. Se você estiver usando Gemini CLI ou Codex, utilize o comando equivalente para invocar uma skill na sua ferramenta.

- Verificar que a Fase 1 detecta corretamente a stack e imprime o resumo
- Verificar que a Fase 2 encontra no mínimo 5 dos problemas documentados na sua análise manual
- Confirmar a execução da Fase 3
- Verificar que a Fase 3:
  - Cria a estrutura de diretórios baseada em MVC
  - A aplicação inicia sem erros
  - Os endpoints originais continuam respondendo
- Salvar o relatório de auditoria (output da Fase 2) em `reports/audit-project-1.md`
- Commitar o código refatorado do projeto no repositório

#### Projeto 2 — ecommerce-api-legacy (Node.js/Express)

Prove que sua skill é reutilizável em outro projeto de backend, mas com stack diferente.

- Copiar a pasta `.claude/skills/refactor-arch/` para dentro de `ecommerce-api-legacy/`
- Invocar a skill:

```bash
cd ../ecommerce-api-legacy
claude "/refactor-arch"
```

- Verificar que as 3 fases executam corretamente neste projeto
- Salvar o relatório em `reports/audit-project-2.md`
- Commitar o código refatorado do projeto no repositório

#### Projeto 3 — task-manager-api (Python/Flask)

Agora o teste com um projeto Python/Flask que já possui alguma organização de camadas (models, routes, services, utils).

- Copiar a pasta `.claude/skills/refactor-arch/` para dentro de `task-manager-api/`
- Invocar a skill:

```bash
cd ../task-manager-api
claude "/refactor-arch"
```

- Verificar que:
  - A Fase 1 detecta corretamente Python/Flask como stack e identifica o domínio de Task Manager
  - A Fase 2 identifica problemas mesmo em um projeto parcialmente organizado
  - A Fase 3 melhora a estrutura sem quebrar a aplicação (todos os endpoints devem continuar respondendo)
- Salvar o relatório em `reports/audit-project-3.md`
- Commitar o código refatorado do projeto no repositório

> **Nota:** Este projeto já possui alguma separação de camadas, mas isso não significa que a arquitetura está adequada. A skill deve identificar tanto problemas de código (segurança, performance, qualidade) quanto oportunidades de melhoria arquitetural. Se houver mudanças estruturais necessárias, a skill deve propô-las e executá-las.

#### Validação

Para cada projeto refatorado, valide o seguinte checklist:

```markdown
## Checklist de Validação

### Fase 1 — Análise
- [ ] Linguagem detectada corretamente
- [ ] Framework detectado corretamente
- [ ] Domínio da aplicação descrito corretamente
- [ ] Número de arquivos analisados condiz com a realidade

### Fase 2 — Auditoria
- [ ] Relatório segue o template definido nos arquivos de referência
- [ ] Cada finding tem arquivo e linhas exatos
- [ ] Findings ordenados por severidade (CRITICAL → LOW)
- [ ] Mínimo de 5 findings identificados
- [ ] Detecção de APIs deprecated incluída (se aplicável)
- [ ] Skill pausa e pede confirmação antes da Fase 3

### Fase 3 — Refatoração
- [ ] Estrutura de diretórios segue padrão MVC
- [ ] Configuração extraída para módulo de config (sem hardcoded)
- [ ] Models criados para abstrair dados
- [ ] Views/Routes separadas para visualização ou roteamento
- [ ] Controllers concentram o fluxo da aplicação
- [ ] Error handling centralizado
- [ ] Entry point claro
- [ ] Aplicação inicia sem erros
- [ ] Endpoints originais respondem corretamente
```

> **Dica:** Se a skill não detectou problemas suficientes ou a refatoração falhou, ajuste os arquivos de referência e execute novamente. É normal precisar de 2-4 iterações.

## Entregável

Repositório público no GitHub (fork do repositório base) contendo:

- Skill completa em `.claude/skills/refactor-arch/` (dentro dos 3 projetos)
- Código refatorado dos 3 projetos (resultado da execução da Fase 3, commitado no repositório)
- Relatórios de auditoria em `reports/` (3 arquivos)
- `README.md` atualizado

### Estrutura do repositório

Faça um fork do repositório base contendo os três projetos com code smells.

> **Nota:** A estrutura abaixo usa Claude Code como exemplo (`.claude/skills/`). Se estiver usando outra ferramenta, adapte os caminhos conforme a convenção dela.

```
desafio-skills/
├── README.md                              # Sua documentação
│
├── code-smells-project/                   # Projeto 1 — Python/Flask (API de E-commerce)
│   ├── .claude/
│   │   └── skills/
│   │       └── refactor-arch/             # ← SUA SKILL AQUI
│   │           ├── SKILL.md
│   │           └── (arquivos de referência)
│   ├── app.py
│   ├── controllers.py
│   ├── models.py
│   ├── database.py
│   └── requirements.txt
│
├── ecommerce-api-legacy/                  # Projeto 2 — Node.js/Express (LMS API com checkout)
│   ├── .claude/
│   │   └── skills/
│   │       └── refactor-arch/             # ← CÓPIA DA SKILL
│   │           └── ...
│   ├── src/
│   │   ├── app.js
│   │   ├── AppManager.js
│   │   └── utils.js
│   ├── api.http
│   └── package.json
│
├── task-manager-api/                      # Projeto 3 — Python/Flask (API de Task Manager)
│   ├── .claude/
│   │   └── skills/
│   │       └── refactor-arch/             # ← CÓPIA DA SKILL
│   │           └── ...
│   ├── app.py
│   ├── database.py
│   ├── seed.py
│   ├── requirements.txt
│   ├── models/
│   ├── routes/
│   ├── services/
│   └── utils/
│
└── reports/                               # Relatórios gerados
    ├── audit-project-1.md                 # Saída da Fase 2 no projeto 1
    ├── audit-project-2.md                 # Saída da Fase 2 no projeto 2
    └── audit-project-3.md                 # Saída da Fase 2 no projeto 3
```

**O que você vai criar:**

- `.claude/skills/refactor-arch/` — A skill completa (SKILL.md + arquivos de referência)
- Código refatorado dos 3 projetos — resultado da execução da Fase 3, commitado no repositório
- `reports/audit-project-{1,2,3}.md` — Relatório de auditoria de cada projeto
- `README.md` — Documentação do seu processo

**O que já vem pronto:**

- `code-smells-project/` — API de E-commerce Python/Flask com code smells intencionais
- `ecommerce-api-legacy/` — LMS API Node.js/Express (com fluxo de checkout) e problemas de implementação
- `task-manager-api/` — API de Task Manager Python/Flask com organização parcial e problemas de segurança/qualidade

> **Dica:** Cada projeto contém problemas intencionais de diferentes severidades (CRITICAL, HIGH, MEDIUM, LOW), incluindo falhas de segurança, violações arquiteturais e problemas de qualidade de código. Parte do desafio é identificá-los por conta própria através da análise manual do código.

### README.md deve conter

**A) Seção "Análise Manual":**

- Lista dos problemas identificados manualmente em cada projeto
- Classificação por severidade
- Justificativa de por que cada problema é relevante

**B) Seção "Construção da Skill":**

- Decisões de design: como estruturou o SKILL.md e os arquivos de referência
- Quais anti-patterns incluiu no catálogo e por quê
- Como garantiu que a skill é agnóstica de tecnologia
- Desafios encontrados e como resolveu

**C) Seção "Resultados":**

- Resumo dos relatórios de auditoria dos 3 projetos (quantos findings por severidade em cada)
- Comparação antes/depois da estrutura de cada projeto
- Checklist de validação preenchido para cada projeto
- Screenshots ou logs mostrando as aplicações rodando após refatoração
- Observações sobre como a skill se comportou em stacks diferentes

**D) Seção "Como Executar":**

- Pré-requisitos (a ferramenta escolhida — Claude Code, Gemini CLI ou Codex — instalada e configurada)
- Comandos para executar a skill em cada projeto
- Como validar que a refatoração funcionou

### Ordem de execução sugerida

**1. Analisar os projetos manualmente**

Leia o código dos três projetos e documente os problemas encontrados.

**2. Criar a skill**

Escreva o SKILL.md e os arquivos de referência.

**3. Executar nos 3 projetos**

```bash
# Projeto 1
cd code-smells-project
claude "/refactor-arch"

# Projeto 2
cd ../ecommerce-api-legacy
claude "/refactor-arch"

# Projeto 3
cd ../task-manager-api
claude "/refactor-arch"
```

Salve a saída da Fase 2 de cada projeto em `reports/audit-project-{1,2,3}.md`.

**4. Iterar**

Se a skill não detectou problemas suficientes ou a refatoração falhou, ajuste os arquivos de referência e execute novamente. É normal precisar de 2-4 iterações.

## Critérios de Aceite

A skill deve atingir os seguintes mínimos em **todos os 3 projetos**:

| Critério | Requisito |
|---|---|
| Fase 1 detecta stack corretamente | OBRIGATÓRIO (3/3 projetos) |
| Fase 2 encontra >= 5 findings | OBRIGATÓRIO (3/3 projetos) |
| Fase 2 inclui pelo menos 1 CRITICAL ou HIGH | OBRIGATÓRIO (3/3 projetos) |
| Fase 3 aplicação funciona após refatoração | OBRIGATÓRIO (3/3 projetos) |

**IMPORTANTE:** Todos os critérios devem ser atingidos nos 3 projetos, não apenas em um!

> **Sobre o projeto 3 (task-manager-api):** Este projeto já possui alguma organização. "aplicação funciona" significa que a API inicia sem erros e todos os endpoints continuam respondendo corretamente.

## Referências

- [Claude Code: Skills](https://docs.anthropic.com/en/docs/claude-code/skills) — Documentação oficial sobre como criar e estruturar Skills
- [Claude Code: Overview](https://docs.anthropic.com/en/docs/claude-code/overview) — Visão geral do Claude Code e suas capacidades
- [The Complete Guide to Building Skills for Claude (PDF)](https://resources.anthropic.com/hubfs/The-Complete-Guide-to-Building-Skill-for-Claude.pdf) — Guia completo da Anthropic sobre construção de Skills
- [Equipping Agents for the Real World with Agent Skills](https://claude.com/blog/equipping-agents-for-the-real-world-with-agent-skills) — Blog oficial da Anthropic sobre Agent Skills

---

## Dicas Finais

- **Comece pela análise manual** — entender os problemas profundamente é essencial para criar uma skill que os detecte.
- **O SKILL.md é um prompt** — ele instrui o agente sobre o que fazer, enquanto os arquivos de referência fornecem o conhecimento de domínio.
- **Seja específico nos sinais de detecção** — "código ruim" não ajuda; "query SQL dentro de loop for" é acionável.
- **Teste incrementalmente** — não tente criar a skill perfeita de primeira.
- **A skill deve ser copiável** — se ela só funciona em um projeto específico, está acoplada demais. Teste nos 3 projetos para validar.
- **Projetos diferentes exigem adaptação** — a Fase 3 de um projeto já parcialmente organizado não vai ter as mesmas transformações de um monolito. Sua skill deve se adaptar ao contexto.
- **Pedir confirmação na Fase 2 é obrigatório** — o humano deve revisar o relatório antes de qualquer modificação.
- **Consulte as referências do curso** — revise a documentação oficial da ferramenta escolhida e os materiais das aulas para relembrar a estrutura e anatomia de uma skill.

---

# Entrega — Skill `refactor-arch`

Esta seção documenta a solução: análise manual, construção da skill, resultados nos 3 projetos e como executar.

- **Skill:** `.claude/skills/refactor-arch/` (idêntica nos 3 projetos) — [`SKILL.md`](code-smells-project/.claude/skills/refactor-arch/SKILL.md) + 5 arquivos em `references/`
- **Relatórios de auditoria (saída da Fase 2):** [`reports/audit-project-1.md`](reports/audit-project-1.md), [`reports/audit-project-2.md`](reports/audit-project-2.md), [`reports/audit-project-3.md`](reports/audit-project-3.md)
- **Logs de validação (antes/depois):** [`reports/logs/`](reports/logs)
- **Smoke tests usados na validação:** [`scripts/`](scripts)

## A) Análise Manual

Leitura completa do código dos 3 projetos antes de escrever a skill. Linhas conferidas no código original (ver commit inicial).

### Projeto 1 — `code-smells-project` (Python/Flask, API de E-commerce)

| # | Severidade | Problema | Onde | Por que é relevante |
|---|---|---|---|---|
| 1 | CRITICAL | SQL Injection em todas as queries (concatenação de strings) | `models.py` (login `:110`, busca `:291-297`, pedidos `:140-165`…) | Bypass de login comprovado: `' OR '1'='1' --` autentica como admin |
| 2 | CRITICAL | Endpoints `/admin/query` (SQL arbitrário) e `/admin/reset-db` sem autenticação | `app.py:47-79` | Qualquer cliente lê/apaga todo o banco |
| 3 | CRITICAL | `SECRET_KEY` hardcoded e devolvida em `/health` | `app.py:7`, `controllers.py:289` | Segredo vaza pelo repositório e pela API |
| 4 | CRITICAL | Senhas em texto puro (seed, `login_usuario`, `criar_usuario`) | `database.py:73-79`, `models.py:105-130` | Vazamento do banco = todas as credenciais |
| 5 | CRITICAL | God files: `models.py` mistura SQL, regras (desconto, estoque) e formatação de 4 domínios | `models.py:1-314` | Sem testes isolados, qualquer mudança afeta tudo |
| 6 | HIGH | Conexão global mutável compartilhada entre threads | `database.py:4-10` | Race conditions, estado oculto |
| 7 | HIGH | `criar_pedido` sem transação (estoque/itens em passos soltos) | `models.py:133-168` | Pedidos parciais e estoque inconsistente |
| 8 | HIGH | `/usuarios` devolve `senha`; `/health` devolve `debug`/`db_path` | `models.py:72-103`, `controllers.py:286-289` | Exposição de dados sensíveis |
| 9 | MEDIUM | N+1 em listagem de pedidos (`cursor2`/`cursor3`) | `models.py:171-232` | Queries crescem com pedidos × itens |
| 10 | MEDIUM | Mapeamento row→dict e validação de produto duplicados (create × update divergentes) | `models.py:4-40`, `controllers.py:24-96` | Correção precisa ser replicada |
| 11 | MEDIUM | `try/except` em cada handler devolvendo `str(e)` | `controllers.py` inteiro | Vaza detalhes internos e erros inconsistentes |
| 12 | LOW | Faixas de desconto/status/categorias como literais | `models.py:256-262`, `controllers.py:52,242` | Regras de negócio escondidas |
| 13 | LOW | `print` como log e "notificações" simuladas com `print` | `controllers.py:208-210` | Sem níveis; acoplamento do controller |

### Projeto 2 — `ecommerce-api-legacy` (Node.js/Express, LMS com checkout)

| # | Severidade | Problema | Onde | Por que é relevante |
|---|---|---|---|---|
| 1 | CRITICAL | Credenciais e chave `pk_live_…` do gateway hardcoded | `utils.js:2-5` | Segredos de produção no repositório |
| 2 | CRITICAL | God Class `AppManager` (DB + schema + rotas + regras + SQL) | `AppManager.js:4-141` | Nada testável isoladamente |
| 3 | CRITICAL | `badCrypto` (base64 repetido, 10.000 iterações síncronas) e senha padrão `"123456"` | `utils.js:17-23`, `AppManager.js:68` | Senhas reversíveis; bloqueia o event loop |
| 4 | CRITICAL | `DELETE /api/users/:id` e relatório financeiro sem autenticação | `AppManager.js:80-137` | Qualquer um apaga contas e lê receita |
| 5 | HIGH | Log do número completo do cartão e da chave do gateway | `AppManager.js:45` | Dados PCI/segredos em logs |
| 6 | HIGH | Estado global (`globalCache`, `totalRevenue` exportado por valor) | `utils.js:9-25` | Estado oculto e enganoso |
| 7 | HIGH | Delete deixa matrículas/pagamentos órfãos; checkout sem transação | `AppManager.js:49-62,131-137` | Dados inconsistentes (a própria resposta admite) |
| 8 | MEDIUM | N+1 + callback hell com contadores manuais no relatório (ordem não determinística) | `AppManager.js:80-128` | Difícil de ler, resposta pode nunca ser enviada |
| 9 | MEDIUM | Erros em texto puro e `err` ignorado em vários callbacks | `AppManager.js:38-60,133` | Falhas silenciosas |
| 10 | LOW | Nomes `u`, `e`, `p`, `cid`, `cc`; `utils.js` guardando config | `AppManager.js:29-33` | Legibilidade |
| 11 | LOW | Dead code (`totalRevenue`, `dbUser`, `dbPass`) e magic numbers (`10000`, `"4"`) | `utils.js`, `AppManager.js:46` | Ruído e regras escondidas |

### Projeto 3 — `task-manager-api` (Python/Flask, parcialmente organizado)

| # | Severidade | Problema | Onde | Por que é relevante |
|---|---|---|---|---|
| 1 | CRITICAL | `SECRET_KEY` e credenciais SMTP hardcoded | `app.py:13`, `services/notification_service.py:7-10` | Segredos versionados |
| 2 | CRITICAL | Senhas com MD5 sem sal; token "fake-jwt-token-<id>" | `models/user.py:27-32`, `routes/user_routes.py:210` | Hash quebrável; token forjável |
| 3 | CRITICAL | Nenhuma rota exige autenticação: criar `role: admin`, alterar `role`, deletar usuários/tasks/categorias | `routes/user_routes.py`, `task_routes.py:226`, `report_routes.py:212` | Escalada de privilégio trivial |
| 4 | HIGH | `to_dict()` do usuário devolve o hash da senha em 4 endpoints | `models/user.py:21` | Exposição de credenciais |
| 5 | HIGH | Rotas com lógica de negócio, queries e commits (não há controllers) | `routes/*.py` | Lógica não testável, regras divergentes |
| 6 | HIGH | `app.run(debug=True, host='0.0.0.0')`, CORS aberto e `create_all()` no import | `app.py:15,30-34` | Debugger exposto na rede |
| 7 | MEDIUM | N+1 em `/tasks`, `/users`, `/categories` e resumo de relatórios | `task_routes.py:41-58`, `report_routes.py:53-65,163` | Latência cresce com os dados |
| 8 | MEDIUM | Regra "atrasada" copiada em 6 lugares apesar de `Task.is_overdue` existir | `task_routes.py:30,71,284`, `user_routes.py:171`, `report_routes.py:34,132` | Correção em um ponto não chega aos demais |
| 9 | MEDIUM | `except:` genérico e validações ausentes (`int()` de query string → 500) | `task_routes.py:62,137,261` | Erros mascarados e 500 em entrada inválida |
| 10 | MEDIUM | APIs deprecated: `datetime.utcnow()` (~20×) e `Model.query.get()` (~17×) | vários | Quebram em versões futuras |
| 11 | LOW | Imports/helpers mortos, magic numbers, `print`, CRUD de categorias dentro de `report_routes.py` | `utils/helpers.py`, `routes/` | Ruído e baixa descobribilidade |

## B) Construção da Skill

### Decisões de design

- **`SKILL.md` = prompt de orquestração; `references/` = conhecimento.** O `SKILL.md` define só o *processo* (3 fases, banners de saída, regras de ouro) e manda o agente ler o arquivo de referência certo antes de cada fase. Assim o conhecimento cresce sem inflar o prompt principal.
- **5 áreas obrigatórias → 5 arquivos:**

| Arquivo | Fase | Conteúdo |
|---|---|---|
| `project-analysis.md` | 1 | Tabelas de heurísticas: manifest → linguagem, dependência + assinatura de código → framework, sinais de banco/ORM, mapeamento de responsabilidades por arquivo, inventário de endpoints |
| `anti-patterns-catalog.md` | 2 | 21 anti-patterns (AP-01…AP-21) com severidade, sinais de detecção, impacto, ligação com o playbook, tabela de APIs deprecated por stack e comandos de triagem |
| `report-template.md` | 2 | Formato exato do relatório, regras (ordem por severidade, arquivo:linhas, contagens), exemplo |
| `mvc-guidelines.md` | 3 | Responsabilidades de cada camada, regra de dependência, regras transversais e layouts-alvo por stack (Flask plano, Flask já em camadas, Express, Spring, Go, Django, Laravel) |
| `refactoring-playbook.md` | 3 | 15 padrões de transformação (P1–P15) com exemplos antes/depois em Python e JavaScript |

- **Pausa obrigatória:** o `SKILL.md` proíbe tocar em qualquer arquivo antes do "Proceed with refactoring (Phase 3)? [y/n]" e encerra a execução se a resposta não for um "sim" explícito.
- **Contrato preservado:** a Fase 3 captura um baseline (boot + todos os endpoints) *antes* de alterar código e compara depois; só mudanças de segurança/correção catalogadas são permitidas e precisam ser listadas.
- **Validação obrigatória:** boot real, chamada de todos os endpoints mapeados na Fase 1 e re-varredura do catálogo (zero CRITICAL/HIGH) antes de declarar sucesso.

### Anti-patterns incluídos e por quê

| Severidade | Anti-patterns |
|---|---|
| CRITICAL | AP-01 credenciais hardcoded · AP-02 SQL injection · AP-03 God Class/File · AP-04 endpoints perigosos sem auth · AP-05 armazenamento fraco de senha/cripto caseira |
| HIGH | AP-06 lógica de negócio em controllers/rotas · AP-07 estado global mutável · AP-08 exposição de dados sensíveis · AP-09 acoplamento sem DI · AP-10 falta de transações/integridade · AP-11 configuração insegura (debug, host) |
| MEDIUM | AP-12 N+1 · AP-13 duplicação · AP-14 validação ausente · AP-15 tratamento de erro ad-hoc · AP-16 callback hell · AP-17 APIs deprecated |
| LOW | AP-18 magic numbers · AP-19 nomes ruins · AP-20 `print`/`console.log` como log · AP-21 código morto |

Escolhi esse conjunto porque cada item apareceu na análise manual dos três projetos (a análise veio *antes* do catálogo) e porque cobre a escala MVC/SOLID do enunciado. APIs deprecated ganharam item próprio (AP-17) com tabela por stack: `datetime.utcnow()`, `Model.query.get()`, `new Buffer()`, `ioutil`, etc.

### Como garanti que a skill é agnóstica de tecnologia

1. Os **sinais de detecção** são descritos por comportamento ("query montada com `+`/f-string/template literal com dado da requisição", "variável de módulo mutável exportada") e não por API de um framework; exemplos Flask/Express aparecem só como ilustração.
2. A detecção de stack é **dirigida por tabela** (manifest + assinatura de código); adicionar Spring/Go/Laravel é acrescentar uma linha, não mudar o processo.
3. As **guidelines MVC** definem papéis e regra de dependência independentes de linguagem e só depois mapeiam para layouts idiomáticos de cada stack.
4. O **playbook** traz cada transformação em duas linguagens (Python e JavaScript) para mostrar que o padrão é o mesmo.
5. A mesma skill (cópia idêntica, verificada com `diff -r`) rodou em Flask plano, Flask já em camadas e Express.

### Desafios encontrados e soluções

| Desafio | Solução |
|---|---|
| macOS ocupa a porta 5000 (AirPlay) → baseline retornava 403 | Skill manda escolher porta livre; entry points passaram a ler `PORT` do ambiente |
| `hashlib.scrypt` ausente no Python 3.9/LibreSSL (padrão do `werkzeug`) quebrou o seed | Playbook P6 passou a usar `pbkdf2:sha256` explicitamente e a documentar o motivo |
| Proteger endpoints perigosos sem quebrar o contrato | P8 (A): remover o que não tem forma segura (`/admin/query`) e proteger o resto com token configurado por ambiente (403 se não configurado) |
| Skill aplicou só parte do AP-04 (deletes admin) e deixou `DELETE /tasks/<id>` e `PUT /users/<id>` anônimos | P8 ampliado (B: auth em toda rota de escrita; C: dono-ou-admin) e Fase 3 com checklist por CRITICAL, validado com requisições negativas (401/403) em cada rota de escrita |
| Projeto 3 já em camadas: transformações diferentes de um monolito | `mvc-guidelines.md` tem layout específico "já em camadas" (adicionar `controllers/`, afinar rotas, mover regras para models) |
| Node com driver de callbacks e uma única conexão: transações podiam intercalar | P11/P15: wrapper promisificado com fila que serializa transações |
| Relatório do projeto 2 tinha ordem não determinística (ordem de conclusão dos callbacks) | Um `JOIN` ordenado por curso/matrícula |

## C) Resultados

### Resumo dos relatórios de auditoria

| Projeto | Stack | CRITICAL | HIGH | MEDIUM | LOW | Total |
|---|---|---|---|---|---|---|
| 1 — code-smells-project | Python + Flask 3.1.1 | 5 | 6 | 4 | 4 | **19** |
| 2 — ecommerce-api-legacy | Node.js + Express 4 | 4 | 5 | 4 | 4 | **17** |
| 3 — task-manager-api | Python + Flask 3.0 + SQLAlchemy | 3 | 5 | 5 | 4 | **17** |

### Comparação antes/depois

**Projeto 1** — 4 arquivos planos (~780 linhas) → 9 pacotes MVC

```
ANTES                         DEPOIS
app.py (rotas+admin+SQL)      app.py (composition root, 27 linhas)
controllers.py (292)          config/settings.py
models.py (314, SQL+regras)   database/{connection,schema,seed,bootstrap}.py
database.py (conexão global)  models/{produto,usuario,pedido,sistema}_model.py
                              controllers/{produto,usuario,pedido,relatorio,sistema}_controller.py
                              views/routes.py · middlewares/error_handler.py
                              services/{password,notification}_service.py · utils/{errors,validators}.py
```

**Projeto 2** — `AppManager.js` (God Class, 141 linhas) + `utils.js` → 8 camadas

```
ANTES                         DEPOIS
src/app.js                    src/app.js (composition root)
src/AppManager.js             src/config/settings.js
src/utils.js                  src/database/{connection,schema}.js
                              src/models/{user,course,enrollment,payment,auditLog,report}Model.js
                              src/controllers/{checkout,report,user}Controller.js
                              src/views/routes.js
                              src/middlewares/{errorHandler,adminAuth,asyncHandler}.js
                              src/services/{paymentGateway,passwordService}.js · src/utils/{errors,logger}.js
```

**Projeto 3** — `models/ routes/ services/ utils/` com rotas gordas → camada `controllers/` e rotas finas

```
ANTES                         DEPOIS
app.py (config+create_all)    app.py (create_app factory)
routes/* (lógica+ORM, 733 l.) routes/* (só URL → controller, 5 blueprints)
models/* (anêmicos)           controllers/{task,user,category,report,system}_controller.py
services/notification (órfão) models/* (regras: is_overdue, queries, agregações)
utils/helpers (código morto)  config/settings.py · middlewares/{auth,error_handler}.py
                              services/{auth,notification}_service.py · utils/{helpers,validators,errors}.py
```

### Checklist de validação

**Projeto 1 — code-smells-project**

```markdown
### Fase 1 — Análise
- [x] Linguagem detectada corretamente (Python)
- [x] Framework detectado corretamente (Flask 3.1.1)
- [x] Domínio da aplicação descrito corretamente (E-commerce: produtos, usuários, pedidos)
- [x] Número de arquivos analisados condiz com a realidade (4)
### Fase 2 — Auditoria
- [x] Relatório segue o template definido nos arquivos de referência
- [x] Cada finding tem arquivo e linhas exatos
- [x] Findings ordenados por severidade (CRITICAL → LOW)
- [x] Mínimo de 5 findings identificados (19)
- [x] Detecção de APIs deprecated incluída (nenhuma encontrada; registrado no relatório)
- [x] Skill pausa e pede confirmação antes da Fase 3
### Fase 3 — Refatoração
- [x] Estrutura de diretórios segue padrão MVC
- [x] Configuração extraída para módulo de config (sem hardcoded)
- [x] Models criados para abstrair dados
- [x] Views/Routes separadas para visualização ou roteamento
- [x] Controllers concentram o fluxo da aplicação
- [x] Error handling centralizado
- [x] Entry point claro
- [x] Aplicação inicia sem erros
- [x] Endpoints originais respondem corretamente (25/25)
```

**Projeto 2 — ecommerce-api-legacy**

```markdown
### Fase 1 — Análise
- [x] Linguagem detectada corretamente (JavaScript/Node.js)
- [x] Framework detectado corretamente (Express 4.18)
- [x] Domínio da aplicação descrito corretamente (LMS com checkout)
- [x] Número de arquivos analisados condiz com a realidade (3)
### Fase 2 — Auditoria
- [x] Relatório segue o template definido nos arquivos de referência
- [x] Cada finding tem arquivo e linhas exatos
- [x] Findings ordenados por severidade (CRITICAL → LOW)
- [x] Mínimo de 5 findings identificados (17)
- [x] Detecção de APIs deprecated incluída (nenhuma encontrada; registrado no relatório)
- [x] Skill pausa e pede confirmação antes da Fase 3
### Fase 3 — Refatoração
- [x] Estrutura de diretórios segue padrão MVC
- [x] Configuração extraída para módulo de config (sem hardcoded)
- [x] Models criados para abstrair dados
- [x] Views/Routes separadas para visualização ou roteamento
- [x] Controllers concentram o fluxo da aplicação
- [x] Error handling centralizado
- [x] Entry point claro
- [x] Aplicação inicia sem erros
- [x] Endpoints originais respondem corretamente (8/8)
```

**Projeto 3 — task-manager-api**

```markdown
### Fase 1 — Análise
- [x] Linguagem detectada corretamente (Python)
- [x] Framework detectado corretamente (Flask 3.0 + SQLAlchemy)
- [x] Domínio da aplicação descrito corretamente (Task Manager)
- [x] Número de arquivos analisados condiz com a realidade (15)
### Fase 2 — Auditoria
- [x] Relatório segue o template definido nos arquivos de referência
- [x] Cada finding tem arquivo e linhas exatos
- [x] Findings ordenados por severidade (CRITICAL → LOW)
- [x] Mínimo de 5 findings identificados (17), com problemas mesmo no projeto já organizado
- [x] Detecção de APIs deprecated incluída (AP-17: utcnow, Query.get)
- [x] Skill pausa e pede confirmação antes da Fase 3
### Fase 3 — Refatoração
- [x] Estrutura de diretórios segue padrão MVC
- [x] Configuração extraída para módulo de config (sem hardcoded)
- [x] Models criados para abstrair dados
- [x] Views/Routes separadas para visualização ou roteamento
- [x] Controllers concentram o fluxo da aplicação
- [x] Error handling centralizado
- [x] Entry point claro
- [x] Aplicação inicia sem erros
- [x] Endpoints originais respondem corretamente (27/27)
```

### Evidências (logs das aplicações rodando após a refatoração)

Logs completos em [`reports/logs/`](reports/logs) (`*-smoke-before.txt` = código original, `*-smoke-after.txt` = refatorado). Trechos:

```text
# Projeto 1 — antes: SQL injection no login (marcado FAIL pelo smoke test); depois: corrigido
FAIL POST   /login -> 200   {"dados": {"email": "admin@loja.com", ...}, "mensagem": "Login OK"}     (antes)
OK   POST   /login -> 401   {"erro": "Email ou senha inválidos", "sucesso": false}                   (depois)
RESULT: 25/25 checks passed                                                                           (depois)

# Projeto 2 — relatório determinístico; delete deixa de gerar órfãos
GET /api/admin/financial-report (depois do DELETE)
  antes:  [{"course":"Clean Architecture","revenue":997,"students":[{"student":"Unknown", ...}]}, ...]
  depois: [{"course":"Clean Architecture","revenue":0,"students":[]}, {"course":"Docker","revenue":497, ...}]
RESULT: 8/8 checks passed

# Projeto 3 — mesmos 27 endpoints; hash de senha deixa de vazar e o token passa a ser assinado
POST /login -> 200   {"token": "eyJ1c2VyX2lkIjoxfQ.auo1Xg.…", "user": {"email": "joao@email.com", ...sem password...}}
RESULT: 27/27 checks passed
```

### Mudanças de contrato (somente segurança/correção, previstas na Fase 2)

| Projeto | Mudança | Motivo |
|---|---|---|
| 1 | `senha` não é mais retornada em `/usuarios`; `/health` não expõe `secret_key`/`debug`/`db_path`; `POST /admin/query` removido; `POST /admin/reset-db` exige `X-Admin-Token`; erros ganham `"sucesso": false`; `PUT /pedidos/<id>/status` de pedido inexistente → 404 | AP-01/04/08/15 |
| 2 | `GET /api/admin/financial-report` e `DELETE /api/users/:id` exigem `X-Admin-Token`; pagamento recusado não cria mais o usuário; senha obrigatória para novo usuário; delete remove matrículas/pagamentos; relatório ordenado por curso | AP-04/05/10/16 |
| 3 | `password` removido das respostas; `token` agora é assinado (itsdangerous); **todas as rotas de escrita exigem Bearer** (401 sem token): `PUT /users/<id>` só pelo próprio usuário ou admin (inclui troca de senha), `PUT/DELETE /tasks/<id>` só pelo dono ou admin (task sem dono: admin), `POST /tasks` não-admin só cria para si, `DELETE /users/<id>` e `POST/PUT/DELETE /categories` só admin, criar usuário com `role` ≠ `user` e alterar `role`/`active` exigem admin; categoria removida desvincula suas tasks; **rodar `python seed.py` de novo** (hash novo) | AP-04/05/08/10 |

### Observações sobre o comportamento em stacks diferentes

- **Flask plano (projeto 1):** o maior ganho foi separar o `models.py` e eliminar as 15+ queries concatenadas; o baseline provou a injeção real antes da correção.
- **Express (projeto 2):** as mesmas fases funcionaram trocando só os sinais (`console.log`, callbacks aninhados, export por valor). O padrão de erro do projeto (texto puro) foi mantido pelo handler central para não quebrar o contrato.
- **Flask já em camadas (projeto 3):** a Fase 2 achou problemas que não são de "arquivo gigante" (regra duplicada em 6 rotas, N+1 via ORM, APIs deprecated) e a Fase 3 foi *aditiva* (criar `controllers/`, afinar `routes/`, mover regras para os models) em vez de reestruturar do zero.
- **Limitação honesta:** a validação de boot depende de o agente conseguir executar o processo; não há suíte de testes automatizada nos projetos, então a verificação foi por baseline + smoke tests de todos os endpoints.
- **Como esta execução foi feita:** não havia CLI `claude`/`gemini`/`codex` neste ambiente. Um agente (Copilot) executou as 3 fases da skill manualmente em cada projeto — o `/refactor-arch` em si deve ser reexecutado na ferramenta escolhida para confirmar a saída. A confirmação da Fase 2 foi dada pela instrução de seguir este README.

## D) Como Executar

### Pré-requisitos

- Uma das ferramentas aceitas instalada e autenticada: **Claude Code** (`npm i -g @anthropic-ai/claude-code`), Gemini CLI ou OpenAI Codex. Os exemplos usam Claude Code (`.claude/skills/refactor-arch/`).
- Python 3.9+ e `pip` (projetos 1 e 3); Node.js 18+ e `npm` (projeto 2).
- No macOS, a porta 5000 costuma estar ocupada pelo AirPlay Receiver: use `PORT=5001` nos projetos Flask.

### Rodar a skill em cada projeto

```bash
# Projeto 1
cd code-smells-project
claude "/refactor-arch"

# Projeto 2
cd ../ecommerce-api-legacy
claude "/refactor-arch"

# Projeto 3
cd ../task-manager-api
claude "/refactor-arch"
```

A skill imprime a Fase 1, o relatório da Fase 2 e pergunta `Proceed with refactoring (Phase 3)? [y/n]`. Responda `y` para refatorar. Salve a saída da Fase 2 em `reports/audit-project-N.md`.

### Subir as aplicações (código já refatorado)

```bash
# Projeto 1  (http://localhost:5000, ou PORT=5001)
cd code-smells-project && python -m venv .venv && .venv/bin/pip install -r requirements.txt
PORT=5001 ADMIN_TOKEN=dev-token .venv/bin/python app.py

# Projeto 2  (http://localhost:3000)
cd ecommerce-api-legacy && npm install
ADMIN_TOKEN=dev-token npm start

# Projeto 3  (http://localhost:5000, ou PORT=5001)
cd task-manager-api && python -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/python seed.py && PORT=5001 .venv/bin/python app.py
```

### Validar que a refatoração funcionou

Com a aplicação no ar, rode o smoke test correspondente (somente stdlib do Python) em outro terminal:

```bash
cd scripts
python smoke_project1.py http://localhost:5001              # espera: RESULT: 25/25 checks passed
ADMIN_TOKEN=dev-token python smoke_project2.py http://localhost:3000   # espera: RESULT: 8/8 checks passed
python smoke_project3.py http://localhost:5001              # espera: RESULT: 27/27 + SECURITY: 28/28 checks passed
```

Cada script chama todos os endpoints originais, imprime status e corpo e termina com código de saída ≠ 0 se algum status divergir. Compare com os logs `reports/logs/*-before.txt` para ver as únicas diferenças esperadas (as mudanças de contrato listadas acima).