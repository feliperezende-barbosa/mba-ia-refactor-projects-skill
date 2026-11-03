# task-manager-api

API de Task Manager em Python/Flask usada como entrada do desafio `refactor-arch`. Diferente dos outros projetos, este já possui alguma separação de camadas (`models/`, `routes/`, `services/`, `utils/`), mas ainda contém problemas arquiteturais e de qualidade.

## Como rodar

```bash
pip install -r requirements.txt
python seed.py
python app.py
```

A aplicação sobe em `http://localhost:5000`. O `seed.py` popula o banco SQLite (`tasks.db`) com usuários, categorias e tasks de exemplo — **rode-o antes do primeiro boot**, caso contrário os endpoints vão retornar listas vazias.

## Estrutura (após `/refactor-arch`)

```
app.py                  # composition root (create_app)
config/settings.py      # ambiente + constantes (status, roles, limites)
database.py             # SQLAlchemy + PersistenceMixin
models/                 # entidades + regras de domínio + queries
controllers/            # fluxo, validação, orquestração
routes/                 # URL → controller (blueprints finos)
middlewares/            # error_handler e auth (Bearer token)
services/               # auth (token assinado) e notificações (SMTP opcional)
utils/                  # helpers, erros de domínio, validadores
```

Configuração via ambiente/`.env`: veja `.env.example`. O login (`POST /login`) devolve um token assinado (`Authorization: Bearer <token>`); `DELETE /users/<id>`, `DELETE /categories/<id>`, criação de usuário com `role` ≠ `user` e alteração de `role`/`active` exigem token de **admin** (seed: `joao@email.com` / `1234`). Após a refatoração, senhas passam a ser guardadas com hash salgado: **rode `python seed.py` novamente** em bancos antigos.
