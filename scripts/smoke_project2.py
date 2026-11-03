"""Smoke test do projeto 2 (ecommerce-api-legacy). Uso: python smoke_project2.py [base_url]"""
import sys
from smoke_common import run

BASE = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:3000"

STEPS = [
    ("POST", "/api/checkout", {"usr": "Guilherme", "eml": "gui@fullcycle.com.br", "pwd": "senhaforte", "c_id": 2, "card": "4111222233334444"}, 200),
    ("POST", "/api/checkout", {"usr": "João", "eml": "joao@teste.com", "pwd": "123", "c_id": 1, "card": "5111222233334444"}, 400),
    ("POST", "/api/checkout", {"usr": "Leonan", "eml": "leonan@fullcycle.com.br", "c_id": 2, "card": "4000000000000000"}, 200),
    ("POST", "/api/checkout", {"usr": "x"}, 400),
    ("POST", "/api/checkout", {"usr": "x", "eml": "x@x.com", "pwd": "1", "c_id": 99, "card": "4111"}, 404),
    ("GET", "/api/admin/financial-report", None, 200),
    ("DELETE", "/api/users/1", None, 200),
    ("GET", "/api/admin/financial-report", None, 200),
]

if __name__ == "__main__":
    sys.exit(1 if run(BASE, STEPS) else 0)
