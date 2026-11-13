"""Smoke test do projeto 3 (task-manager-api). Uso: python smoke_project3.py [base_url]"""
import sys
from smoke_common import EXTRA_HEADERS, call, run

BASE = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:5000"


def login(email, password):
    status, body = call(BASE, "POST", "/login", {"email": email, "password": password})
    return "Bearer " + body["token"] if status == 200 else None


def authenticate_as_admin():
    """Todas as rotas de escrita exigem Bearer; o fluxo principal roda como admin."""
    token = login("joao@email.com", "1234")
    if token:
        EXTRA_HEADERS["Authorization"] = token


def as_caller(authorization, method, path, body=None):
    """Executa uma chamada com outro Authorization (None = anônimo) e restaura o admin."""
    saved = EXTRA_HEADERS.pop("Authorization", None)
    if authorization:
        EXTRA_HEADERS["Authorization"] = authorization
    try:
        return call(BASE, method, path, body)[0]
    finally:
        EXTRA_HEADERS.pop("Authorization", None)
        if saved:
            EXTRA_HEADERS["Authorization"] = saved


def security_checks():
    """Casos negativos de AP-04: 401 sem token, 403 para não-dono, sucesso para dono/admin."""
    maria = login("maria@email.com", "abcd")
    unowned = call(BASE, "POST", "/tasks", {"title": "Sem dono"})[1]["id"]  # admin: sem user_id = sem dono
    admin_task = call(BASE, "POST", "/tasks", {"title": "Task do admin", "user_id": 1})[1]["id"]
    checks = [
        ("anônimo PUT /users/1 (trocar senha do admin)", None, "PUT", "/users/1", {"password": "hacked"}, 401),
        ("anônimo POST /users role admin", None, "POST", "/users", {"name": "X", "email": "x@x.com", "password": "abcd", "role": "admin"}, 401),
        ("anônimo DELETE /users/2", None, "DELETE", "/users/2", None, 401),
        ("anônimo POST /tasks", None, "POST", "/tasks", {"title": "Anon"}, 401),
        ("anônimo PUT /tasks/1", None, "PUT", "/tasks/1", {"title": "Anon edit"}, 401),
        ("anônimo DELETE /tasks/1", None, "DELETE", "/tasks/1", None, 401),
        ("anônimo POST /categories", None, "POST", "/categories", {"name": "Anon"}, 401),
        ("anônimo PUT /categories/1", None, "PUT", "/categories/1", {"name": "Anon"}, 401),
        ("anônimo DELETE /categories/1", None, "DELETE", "/categories/1", None, 401),
        ("token inválido DELETE /tasks/1", "Bearer invalido", "DELETE", "/tasks/1", None, 401),
        ("usuário PUT /users/1 (senha do admin)", maria, "PUT", "/users/1", {"password": "hacked"}, 403),
        ("usuário DELETE /users/1", maria, "DELETE", "/users/1", None, 403),
        ("usuário PUT /users/2 role admin (auto-promoção)", maria, "PUT", "/users/2", {"role": "admin"}, 403),
        ("usuário POST /users role admin", maria, "POST", "/users", {"name": "X", "email": "x@x.com", "password": "abcd", "role": "admin"}, 403),
        ("usuário DELETE /tasks/<task do admin>", maria, "DELETE", f"/tasks/{admin_task}", None, 403),
        ("usuário PUT /tasks/<task do admin>", maria, "PUT", f"/tasks/{admin_task}", {"title": "Hack"}, 403),
        ("usuário PUT /tasks/<task sem dono>", maria, "PUT", f"/tasks/{unowned}", {"title": "Hack"}, 403),
        ("usuário POST /tasks para outro usuário", maria, "POST", "/tasks", {"title": "Para o admin", "user_id": 1}, 403),
        ("usuário reatribui própria task a outro", maria, "PUT", "/tasks/2", {"user_id": 1}, 403),
        ("usuário POST /categories", maria, "POST", "/categories", {"name": "Nope"}, 403),
        ("usuário DELETE /categories/1", maria, "DELETE", "/categories/1", None, 403),
        ("dono PUT /users/2 (próprio nome)", maria, "PUT", "/users/2", {"name": "Maria S."}, 200),
        ("dono PUT /tasks/2 (própria task)", maria, "PUT", "/tasks/2", {"status": "done"}, 200),
        ("usuário POST /tasks sem user_id (vira dono)", maria, "POST", "/tasks", {"title": "Minha task"}, 201),
        ("admin PUT /users/2 role", "admin", "PUT", "/users/2", {"role": "manager"}, 200),
        ("admin PUT /tasks/<task sem dono>", "admin", "PUT", f"/tasks/{unowned}", {"title": "Admin edit"}, 200),
        ("admin DELETE /tasks/<task do admin>", "admin", "DELETE", f"/tasks/{admin_task}", None, 200),
    ]
    admin = EXTRA_HEADERS.get("Authorization")
    failures = 0
    for label, authorization, method, path, body, expected in checks:
        if authorization == "admin":
            authorization = admin
        status = as_caller(authorization, method, path, body)
        ok = status == expected
        failures += 0 if ok else 1
        print(f"{'OK  ' if ok else 'FAIL'} [security] {label} -> {status} (esperado {expected})")
    admin_still_logs_in = login("joao@email.com", "1234") is not None
    failures += 0 if admin_still_logs_in else 1
    print(f"{'OK  ' if admin_still_logs_in else 'FAIL'} [security] senha do admin permanece válida")
    for task_id in (unowned,):
        call(BASE, "DELETE", f"/tasks/{task_id}")
    print(f"\nSECURITY: {len(checks) + 1 - failures}/{len(checks) + 1} checks passed")
    return failures

STEPS = [
    ("GET", "/", None, 200),
    ("GET", "/health", None, 200),
    ("GET", "/tasks", None, 200),
    ("GET", "/tasks/1", None, 200),
    ("GET", "/tasks/999", None, 404),
    ("GET", "/tasks/search?q=API&status=pending", None, 200),
    ("GET", "/tasks/search?priority=1", None, 200),
    ("GET", "/tasks/stats", None, 200),
    ("POST", "/tasks", {"title": "Nova task", "priority": 2, "user_id": 1, "category_id": 1, "due_date": "2030-01-01", "tags": ["a", "b"]}, 201),
    ("POST", "/tasks", {"title": "ab"}, 400),
    ("PUT", "/tasks/11", {"status": "done", "priority": 5}, 200),
    ("DELETE", "/tasks/11", None, 200),
    ("GET", "/users", None, 200),
    ("GET", "/users/1", None, 200),
    ("GET", "/users/1/tasks", None, 200),
    ("POST", "/users", {"name": "Teste", "email": "teste@email.com", "password": "abcd1234"}, 201),
    ("POST", "/users", {"name": "Teste", "email": "teste@email.com", "password": "abcd1234"}, 409),
    ("PUT", "/users/4", {"name": "Teste 2", "role": "manager"}, 200),
    ("POST", "/login", {"email": "joao@email.com", "password": "1234"}, 200),
    ("POST", "/login", {"email": "joao@email.com", "password": "errada"}, 401),
    ("DELETE", "/users/4", None, 200),
    ("GET", "/reports/summary", None, 200),
    ("GET", "/reports/user/1", None, 200),
    ("GET", "/categories", None, 200),
    ("POST", "/categories", {"name": "Nova Cat", "color": "#123456"}, 201),
    ("PUT", "/categories/5", {"name": "Cat Editada"}, 200),
    ("DELETE", "/categories/5", None, 200),
]

if __name__ == "__main__":
    authenticate_as_admin()
    failed = run(BASE, STEPS)
    failed += security_checks()
    sys.exit(1 if failed else 0)
