"""Smoke test do projeto 3 (task-manager-api). Uso: python smoke_project3.py [base_url]"""
import sys
from smoke_common import EXTRA_HEADERS, call, run

BASE = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:5000"


def authenticate_as_admin():
    """Rotas administrativas (DELETE de usuário/categoria, alterar role) exigem Bearer de admin."""
    status, body = call(BASE, "POST", "/login", {"email": "joao@email.com", "password": "1234"})
    if status == 200:
        EXTRA_HEADERS["Authorization"] = "Bearer " + body["token"]

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
    sys.exit(1 if run(BASE, STEPS) else 0)
