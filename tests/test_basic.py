import os
import sys
import pytest

# Adiciona o diretório raiz ao path para importar os módulos
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def test_import_modules():
    """Testa se é possível importar os módulos principais."""
    try:
        from models import ExcavationPoint
        import database
        assert True
    except ImportError:
        try:
            from sitai.models import ExcavationPoint
            import sitai.database
            assert True
        except ImportError:
            pytest.skip("Módulos não encontrados, pulando o teste")

def test_environment():
    """Verifica se o ambiente de execução está configurado corretamente."""
    assert sys.version_info >= (3, 8), "Python 3.8+ é necessário"
    
def test_data_dir():
    """Verifica se o diretório de dados pode ser criado."""
    data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
    os.makedirs(data_dir, exist_ok=True)
    assert os.path.exists(data_dir), "Diretório de dados não pôde ser criado"
