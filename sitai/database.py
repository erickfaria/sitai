import sqlite3
import os
import pandas as pd
from datetime import datetime
from sitai.models import ExcavationPoint

DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
DB_PATH = os.path.join(DATA_DIR, 'database.db')

def ensure_data_dir():
    """Garante que o diretório de dados existe"""
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)

def init_db():
    """Inicializa o banco de dados com a tabela necessária"""
    ensure_data_dir()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS excavation_points (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        point_type TEXT NOT NULL,
        latitude REAL NOT NULL,
        longitude REAL NOT NULL,
        altitude REAL NOT NULL,
        description TEXT,
        discovery_date TEXT NOT NULL,
        responsible TEXT NOT NULL,
        srid TEXT NOT NULL
    )
    ''')
    
    conn.commit()
    conn.close()

def create_point(point: ExcavationPoint):
    """Cria um novo ponto de escavação no banco de dados"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute(
        '''
        INSERT INTO excavation_points 
        (point_type, latitude, longitude, altitude, description, discovery_date, responsible, srid)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''',
        (
            point.point_type, 
            point.latitude, 
            point.longitude, 
            point.altitude,
            point.description,
            point.discovery_date.isoformat(),
            point.responsible,
            point.srid
        )
    )
    
    conn.commit()
    point_id = cursor.lastrowid
    conn.close()
    
    return point_id

def get_all_points():
    """Busca todos os pontos de escavação no banco de dados"""
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM excavation_points", conn)
    conn.close()
    return df

def get_point_by_id(point_id: int):
    """Busca um ponto específico pelo ID"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM excavation_points WHERE id = ?", (point_id,))
    result = cursor.fetchone()
    conn.close()
    
    if result:
        columns = [col[0] for col in cursor.description]
        data = dict(zip(columns, result))
        data['discovery_date'] = datetime.fromisoformat(data['discovery_date'])
        return ExcavationPoint(**data)
    return None

def update_point(point: ExcavationPoint):
    """Atualiza um ponto de escavação existente"""
    if not point.id:
        raise ValueError("ID de ponto não especificado para atualização")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute(
        '''
        UPDATE excavation_points 
        SET point_type = ?, latitude = ?, longitude = ?, altitude = ?, 
            description = ?, discovery_date = ?, responsible = ?, srid = ?
        WHERE id = ?
        ''',
        (
            point.point_type, 
            point.latitude, 
            point.longitude, 
            point.altitude,
            point.description,
            point.discovery_date.isoformat(),
            point.responsible,
            point.srid,
            point.id
        )
    )
    
    conn.commit()
    updated = cursor.rowcount > 0
    conn.close()
    
    return updated

def delete_point(point_id: int):
    """Remove um ponto de escavação pelo ID"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("DELETE FROM excavation_points WHERE id = ?", (point_id,))
    
    conn.commit()
    deleted = cursor.rowcount > 0
    conn.close()
    
    return deleted

def search_points(query: str = "", field: str = None):
    """Busca pontos de escavação com base em um termo de pesquisa"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    if field and query:
        sql = f"SELECT * FROM excavation_points WHERE {field} LIKE ?"
        cursor.execute(sql, (f'%{query}%',))
    elif query:
        cursor.execute(
            """
            SELECT * FROM excavation_points 
            WHERE point_type LIKE ? OR description LIKE ? OR responsible LIKE ?
            """, 
            (f'%{query}%', f'%{query}%', f'%{query}%')
        )
    else:
        cursor.execute("SELECT * FROM excavation_points")
    
    columns = [col[0] for col in cursor.description]
    results = [dict(zip(columns, row)) for row in cursor.fetchall()]
    conn.close()
    
    return results
