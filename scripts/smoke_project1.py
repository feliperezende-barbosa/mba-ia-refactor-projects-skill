"""Smoke test do projeto 1 (code-smells-project). Uso: python smoke_project1.py [base_url]"""
import sys
from smoke_common import run

BASE = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:5000"

STEPS = [
    ("GET", "/", None, 200),
    ("GET", "/health", None, 200),
    ("GET", "/produtos", None, 200),
    ("GET", "/produtos/1", None, 200),
    ("GET", "/produtos/999", None, 404),
    ("GET", "/produtos/busca?q=gamer", None, 200),
    ("GET", "/produtos/busca?categoria=moveis&preco_min=100&preco_max=2000", None, 200),
    ("GET", "/produtos/busca?q=%27%20OR%20%271%27%3D%271", None, 200),
    ("POST", "/produtos", {"nome": "Produto Teste", "descricao": "d", "preco": 10.5, "estoque": 5, "categoria": "geral"}, 201),
    ("POST", "/produtos", {"nome": "x", "preco": 1, "estoque": 1}, 400),
    ("PUT", "/produtos/11", {"nome": "Produto Atualizado", "descricao": "d2", "preco": 20, "estoque": 7, "categoria": "livros"}, 200),
    ("DELETE", "/produtos/11", None, 200),
    ("GET", "/usuarios", None, 200),
    ("GET", "/usuarios/1", None, 200),
    ("POST", "/usuarios", {"nome": "Novo", "email": "novo@email.com", "senha": "segredo1"}, 201),
    ("POST", "/login", {"email": "admin@loja.com", "senha": "admin123"}, 200),
    ("POST", "/login", {"email": "admin@loja.com", "senha": "errada"}, 401),
    ("POST", "/login", {"email": "' OR '1'='1' --", "senha": "x"}, 401),
    ("POST", "/pedidos", {"usuario_id": 2, "itens": [{"produto_id": 1, "quantidade": 2}, {"produto_id": 2, "quantidade": 1}]}, 201),
    ("POST", "/pedidos", {"usuario_id": 2, "itens": [{"produto_id": 999, "quantidade": 1}]}, 400),
    ("GET", "/pedidos", None, 200),
    ("GET", "/pedidos/usuario/2", None, 200),
    ("PUT", "/pedidos/1/status", {"status": "aprovado"}, 200),
    ("PUT", "/pedidos/1/status", {"status": "invalido"}, 400),
    ("GET", "/relatorios/vendas", None, 200),
]

if __name__ == "__main__":
    sys.exit(1 if run(BASE, STEPS) else 0)
