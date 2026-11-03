# ecommerce-api-legacy

LMS API (com fluxo de checkout) em Node.js/Express usada como entrada do desafio `refactor-arch`.

## Como rodar

```bash
npm install
npm start
```

A aplicação sobe em `http://localhost:3000`. O banco SQLite é em memória e já carrega seeds automaticamente no boot.

Exemplos de requisições estão em `api.http`.

## Estrutura (após `/refactor-arch`)

```
src/
├── app.js                  # composition root (createApp)
├── config/settings.js      # variáveis de ambiente
├── database/               # wrapper promisificado do sqlite3, schema e seed
├── models/                 # acesso a dados
├── controllers/            # checkout, relatório, usuários
├── views/routes.js         # URL → controller
├── middlewares/            # errorHandler, adminAuth, asyncHandler
├── services/               # gateway de pagamento (simulado), hash de senha (scrypt)
└── utils/                  # logger e erros de domínio
```

Configuração via ambiente: veja `.env.example`. As rotas `GET /api/admin/financial-report` e `DELETE /api/users/:id` exigem o header `X-Admin-Token` igual a `ADMIN_TOKEN` (sem a variável, respondem 403).
