import pytest
from datetime import datetime
import sys
import os

# Adiciona o diretório raiz ao path para importar os módulos
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    from models import ExcavationPoint
except ImportError:
    try:
        from sitai.models import ExcavationPoint
    except ImportError:
        pytest.skip("Módulo ExcavationPoint não encontrado", allow_module_level=True)

def test_excavation_point_creation():
    """Testa a criação de um ponto de escavação."""
    point = ExcavationPoint(
        point_type="Artefato indígena",
        latitude=-3.1190,
        longitude=-60.0217,
        altitude=92.0,
        description="Cerâmica com desenhos geométricos",
        responsible="Dr. Ana Silva",
        discovery_date=datetime.now()
    )
    
    assert point.point_type == "Artefato indígena"
    assert point.latitude == -3.1190
    assert point.longitude == -60.0217
    assert point.altitude == 92.0
    assert point.description == "Cerâmica com desenhos geométricos"
    assert point.responsible == "Dr. Ana Silva"
    assert point.srid == "WGS84"  # valor padrão

def test_latitude_validation():
    """Testa a validação de latitude."""
    with pytest.raises(ValueError):
        ExcavationPoint(
            point_type="Test",
            latitude=100.0,  # Inválido: > 90
            longitude=0.0,
            altitude=0.0,
            description="Test",
            responsible="Test"
        )
    
    with pytest.raises(ValueError):
        ExcavationPoint(
            point_type="Test",
            latitude=-100.0,  # Inválido: < -90
            longitude=0.0,
            altitude=0.0,
            description="Test",
            responsible="Test"
        )

def test_longitude_validation():
    """Testa a validação de longitude."""
    with pytest.raises(ValueError):
        ExcavationPoint(
            point_type="Test",
            latitude=0.0,
            longitude=200.0,  # Inválido: > 180
            altitude=0.0,
            description="Test",
            responsible="Test"
        )
    
    with pytest.raises(ValueError):
        ExcavationPoint(
            point_type="Test",
            latitude=0.0,
            longitude=-200.0,  # Inválido: < -180
            altitude=0.0,
            description="Test",
            responsible="Test"
        )
