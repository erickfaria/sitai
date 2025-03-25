import pytest
import os
import sys
from datetime import datetime
import sqlite3

# Adiciona o diretório raiz ao path para importar os módulos
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    from models import ExcavationPoint
    import database as db
except ImportError:
    try:
        from sitai.models import ExcavationPoint
        import sitai.database as db
    except ImportError:
        pytest.skip("Módulos necessários não encontrados", allow_module_level=True)

@pytest.fixture
def setup_test_db():
    """Configura um banco de dados de teste temporário."""
    # Salva o caminho original
    original_db_path = db.DB_PATH
    
    # Configura um banco de dados de teste
    test_db_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'tests', 'data')
    os.makedirs(test_db_dir, exist_ok=True)
    test_db_path = os.path.join(test_db_dir, 'test_database.db')
    
    # Se o arquivo de teste já existir, remova-o
    if os.path.exists(test_db_path):
        os.remove(test_db_path)
    
    # Substitui o caminho do banco de dados
    db.DB_PATH = test_db_path
    
    # Inicializa o banco de dados de teste
    db.init_db()
    
    yield
    
    # Restaura o caminho original
    db.DB_PATH = original_db_path
    
    # Limpa o arquivo de teste
    if os.path.exists(test_db_path):
        os.remove(test_db_path)

@pytest.mark.parametrize("test_point", [
    {
        "point_type": "Artefato indígena",
        "latitude": -3.1190,
        "longitude": -60.0217,
        "altitude": 92.0,
        "description": "Cerâmica com desenhos geométricos",
        "responsible": "Dr. Ana Silva"
    },
    {
        "point_type": "Antiga cabana indígena",
        "latitude": 0.0,
        "longitude": 0.0,
        "altitude": 150.0,
        "description": "Restos de uma estrutura habitacional",
        "responsible": "Dr. Carlos Souza"
    }
])
def test_create_and_get_point(setup_test_db, test_point):
    """Testa a criação e recuperação de pontos no banco de dados."""
    # Cria um ponto
    point = ExcavationPoint(
        **test_point,
        discovery_date=datetime.now()
    )
    
    # Adiciona ao banco
    point_id = db.create_point(point)
    
    # Verifica se foi criado com sucesso
    assert point_id is not None
    assert point_id > 0
    
    # Recupera o ponto
    retrieved_point = db.get_point_by_id(point_id)
    
    # Verifica se os dados correspondem
    assert retrieved_point is not None
    assert retrieved_point.id == point_id
    assert retrieved_point.point_type == test_point["point_type"]
    assert retrieved_point.latitude == test_point["latitude"]
    assert retrieved_point.longitude == test_point["longitude"]
    assert retrieved_point.altitude == test_point["altitude"]
    assert retrieved_point.description == test_point["description"]
    assert retrieved_point.responsible == test_point["responsible"]

def test_update_point(setup_test_db):
    """Testa a atualização de pontos no banco de dados."""
    # Cria um ponto
    point = ExcavationPoint(
        point_type="Artefato indígena",
        latitude=-3.1190,
        longitude=-60.0217,
        altitude=92.0,
        description="Descrição original",
        responsible="Responsável original",
        discovery_date=datetime.now()
    )
    
    # Adiciona ao banco
    point_id = db.create_point(point)
    
    # Recupera o ponto
    retrieved_point = db.get_point_by_id(point_id)
    
    # Modifica o ponto
    retrieved_point.description = "Descrição atualizada"
    retrieved_point.responsible = "Novo responsável"
    
    # Atualiza no banco
    success = db.update_point(retrieved_point)
    
    # Verifica se foi atualizado com sucesso
    assert success is True
    
    # Recupera novamente
    updated_point = db.get_point_by_id(point_id)
    
    # Verifica se os dados foram atualizados
    assert updated_point.description == "Descrição atualizada"
    assert updated_point.responsible == "Novo responsável"

def test_delete_point(setup_test_db):
    """Testa a exclusão de pontos no banco de dados."""
    # Cria um ponto
    point = ExcavationPoint(
        point_type="Ponto para exclusão",
        latitude=0.0,
        longitude=0.0,
        altitude=0.0,
        description="Este ponto será excluído",
        responsible="Teste",
        discovery_date=datetime.now()
    )
    
    # Adiciona ao banco
    point_id = db.create_point(point)
    
    # Verifica se existe
    assert db.get_point_by_id(point_id) is not None
    
    # Exclui o ponto
    success = db.delete_point(point_id)
    
    # Verifica se foi excluído com sucesso
    assert success is True
    
    # Verifica se não existe mais
    assert db.get_point_by_id(point_id) is None

def test_search_points(setup_test_db):
    """Testa a pesquisa de pontos no banco de dados."""
    # Cria alguns pontos
    points = [
        ExcavationPoint(
            point_type="Cerâmica decorada",
            latitude=1.0,
            longitude=1.0,
            altitude=10.0,
            description="Fragmento de cerâmica com desenhos",
            responsible="Pesquisador A",
            discovery_date=datetime.now()
        ),
        ExcavationPoint(
            point_type="Utensílio de caça",
            latitude=2.0,
            longitude=2.0,
            altitude=20.0,
            description="Ponta de flecha de pedra",
            responsible="Pesquisador B",
            discovery_date=datetime.now()
        ),
        ExcavationPoint(
            point_type="Adorno corporal",
            latitude=3.0,
            longitude=3.0,
            altitude=30.0,
            description="Colar de sementes",
            responsible="Pesquisador A",
            discovery_date=datetime.now()
        )
    ]
    
    # Adiciona ao banco
    for point in points:
        db.create_point(point)
    
    # Testa pesquisa por termo geral
    results = db.search_points("cerâmica")
    assert len(results) == 1
    
    # Testa pesquisa por responsável
    results = db.search_points("Pesquisador A", field="responsible")
    assert len(results) == 2
    
    # Testa pesquisa sem resultados
    results = db.search_points("termo inexistente")
    assert len(results) == 0
