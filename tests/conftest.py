import os
import sys
import pytest

# Adiciona o diretório raiz ao path para importar os módulos
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Configurações globais para os testes
def pytest_configure(config):
    """Configurações globais para os testes."""
    # Marca personalizada para testes que requerem um banco de dados
    config.addinivalue_line("markers", "db: marca testes que precisam de acesso ao banco de dados")

@pytest.fixture
def temp_db_path(tmp_path):
    """Fixture que fornece um caminho temporário para o banco de dados."""
    db_path = tmp_path / "test_database.db"
    return str(db_path)
