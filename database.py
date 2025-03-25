import sqlite3
import os
import pandas as pd
from datetime import datetime
import logging

# Configura o logging para facilitar debug
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Tenta importar o modelo de diferentes locais
try:
    from models import ExcavationPoint
except ImportError:
    try:
        from sitai.models import ExcavationPoint
    except ImportError:
        logger.error("Não foi possível importar o modelo ExcavationPoint")

DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
DB_PATH = os.path.join(DATA_DIR, 'database.db')

def ensure_data_dir():
    """Garante que o diretório de dados existe"""
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
        logger.info(f"Diretório de dados criado: {DATA_DIR}")

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
    logger.info("Banco de dados inicializado com sucesso")

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
    
    logger.info(f"Ponto criado com ID: {point_id}")
    return point_id

def get_all_points():
    """Busca todos os pontos de escavação no banco de dados"""
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM excavation_points", conn)
    conn.close()
    logger.info(f"Consultados {len(df)} pontos do banco de dados")
    return df

def get_point_by_id(point_id: int):
    """Busca um ponto específico pelo ID"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM excavation_points WHERE id = ?", (point_id,))
    result = cursor.fetchone()
    
    if result:
        columns = [col[0] for col in cursor.description]
        data = dict(zip(columns, result))
        data['discovery_date'] = datetime.fromisoformat(data['discovery_date'])
        conn.close()
        logger.info(f"Ponto encontrado com ID: {point_id}")
        return ExcavationPoint(**data)
    
    conn.close()
    logger.warning(f"Ponto não encontrado com ID: {point_id}")
    return None

def update_point(point: ExcavationPoint):
    """Atualiza um ponto de escavação existente"""
    if not point.id:
        logger.error("Tentativa de atualização sem ID")
        raise ValueError("ID de ponto não especificado para atualização")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Primeiro verificamos se o ponto existe
    cursor.execute("SELECT id FROM excavation_points WHERE id = ?", (point.id,))
    if not cursor.fetchone():
        conn.close()
        logger.warning(f"Tentativa de atualizar ponto inexistente com ID: {point.id}")
        return False
    
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
    
    if updated:
        logger.info(f"Ponto atualizado com ID: {point.id}")
    else:
        logger.warning(f"Falha ao atualizar ponto com ID: {point.id}")
    
    return updated

def delete_point(point_id: int):
    """Remove um ponto de escavação pelo ID"""
    logger.info(f"Tentando excluir ponto com ID: {point_id}")
    
    # Validação
    if not isinstance(point_id, int) or point_id <= 0:
        logger.error(f"ID inválido para exclusão: {point_id}")
        return False
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Verificamos se o ponto existe
        cursor.execute("SELECT id FROM excavation_points WHERE id = ?", (point_id,))
        if not cursor.fetchone():
            conn.close()
            logger.warning(f"Tentativa de excluir ponto inexistente com ID: {point_id}")
            return False
        
        # Executa a exclusão
        logger.info(f"Executando DELETE para ponto com ID: {point_id}")
        cursor.execute("DELETE FROM excavation_points WHERE id = ?", (point_id,))
        
        # Verificamos se algo foi afetado
        if cursor.rowcount <= 0:
            logger.warning(f"Nenhuma linha afetada ao excluir ponto com ID: {point_id}")
            conn.close()
            return False
        
        # Commit explícito para garantir que as alterações sejam salvas
        conn.commit()
        logger.info(f"Exclusão confirmada com commit para ID: {point_id}")
        
        conn.close()
        return True
    except Exception as e:
        logger.error(f"Erro ao excluir ponto com ID {point_id}: {str(e)}")
        return False

def search_points(query: str = "", field: str = None):
    """Busca pontos de escavação com base em um termo de pesquisa"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        if field and query:
            sql_query = f"SELECT * FROM excavation_points WHERE {field} LIKE ?"
            cursor.execute(sql_query, (f"%{query}%",))
        elif query:
            sql_query = "SELECT * FROM excavation_points WHERE point_type LIKE ? OR description LIKE ? OR responsible LIKE ?"
            cursor.execute(sql_query, (f"%{query}%", f"%{query}%", f"%{query}%",))
        else:
            cursor.execute("SELECT * FROM excavation_points")
        
        # Obter nomes das colunas
        columns = [col[0] for col in cursor.description]
        
        # Converter resultados em lista de dicionários
        results = []
        for row in cursor.fetchall():
            results.append(dict(zip(columns, row)))
        
        conn.close()
        
        if results:
            logger.info(f"Encontrados {len(results)} pontos com o termo de pesquisa: {query}")
        else:
            logger.info(f"Nenhum ponto encontrado com o termo de pesquisa: {query}")
        
        return results
    except Exception as e:
        logger.error(f"Erro na pesquisa: {str(e)}")
        conn.close()
        return []