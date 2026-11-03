# code-smells-project

API de E-commerce em Python/Flask usada como entrada do desafio `refactor-arch`.

## Como rodar

```bash
pip install -r requirements.txt
python app.py
```

A aplicação sobe em `http://localhost:5000`. O banco SQLite (`loja.db`) é criado automaticamente no primeiro boot, já com produtos e usuários de exemplo.

## Estrutura (após `/refactor-arch`)

```
app.py                  # composition root (create_app)
config/settings.py      # variáveis de ambiente + constantes de negócio
database/               # conexão por requisição, schema e seed
models/                 # acesso a dados (queries parametrizadas)
controllers/            # fluxo, validação e regras
views/routes.py         # URL → controller
middlewares/            # handler de erros central, auth admin
services/               # senha (hash) e notificações
utils/                  # erros de domínio e validadores
```

Configuração via ambiente: veja `.env.example` (`SECRET_KEY`, `FLASK_DEBUG`, `HOST`, `PORT`, `DATABASE_PATH`, `ADMIN_TOKEN`). `POST /admin/reset-db` só funciona com `ADMIN_TOKEN` definido e o header `X-Admin-Token`; `/admin/query` foi removido.
