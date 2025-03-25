from datetime import datetime
from typing import Optional
from pydantic import BaseModel, field_validator, ConfigDict

class ExcavationPoint(BaseModel):
    id: Optional[int] = None
    point_type: str  # Tipo de ponto (cabana, utensílio, artefato, etc.)
    latitude: float
    longitude: float
    altitude: float
    description: str
    discovery_date: datetime = datetime.now()
    responsible: str
    srid: str = "WGS84"  # Sistema de Referência (padrão: WGS84)
    
    model_config = ConfigDict(
        extra="ignore",
        json_schema_extra={
            "example": {
                "point_type": "Artefato indígena",
                "latitude": -3.1190,
                "longitude": -60.0217,
                "altitude": 92.0,
                "description": "Cerâmica com desenhos geométricos encontrada próxima ao rio",
                "responsible": "Dr. Ana Silva",
                "srid": "WGS84"
            }
        }
    )
    
    @field_validator('latitude')
    @classmethod
    def validate_latitude(cls, v):
        if not -90 <= v <= 90:
            raise ValueError('Latitude deve estar entre -90 e 90 graus')
        return v
    
    @field_validator('longitude')
    @classmethod
    def validate_longitude(cls, v):
        if not -180 <= v <= 180:
            raise ValueError('Longitude deve estar entre -180 e 180 graus')
        return v
