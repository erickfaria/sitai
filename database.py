"""
Módulo de gerenciamento de banco de dados para pontos de escavação arqueológica.

Este módulo fornece funções para inicialização e manipulação do banco de dados SQLite
que armazena informações sobre pontos de escavação arqueológica. Implementa operações
CRUD (Create, Read, Update, Delete) e funções de busca.
"""

import sqlite3
import os
import pandas as pd
from datetime import datetime
import logging  # Corrigido: era "loggingnPoint"
from typing import Optional, List, Dict, Any, Union, TypeVar

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constantes
DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
DB_PATH = os.path.join(DATA_DIR, 'database.db')
TABLE_NAME = "excavation_points"

# Definição de tipo para resolução de problemas de tipagem
T = TypeVar('T')

# Definição de classe fallback para quando ExcavationPoint não puder ser importado
class ExcavationPointFallback:
    """Classe de fallback para quando ExcavationPoint não puder ser importado."""
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

# Tenta importar o modelo de diferentes locais
try:
    from sitai.models import ExcavationPoint
except ImportError:
    try:
        from sitai.models import ExcavationPoint
    except ImportError:
        logger.error("Não foi possível importar o modelo ExcavationPoint")
        # Definindo uma classe substituta para evitar erros de execução
        ExcavationPoint = ExcavationPointFallback
        logger.warning("Usando classe de fallback para ExcavationPoint")


def ensure_data_dir() -> None:
    """
    Garante que o diretório de dados existe.

    Cria o diretório de dados se não existir, garantindo que o banco de dados
    possa ser criado e acessado corretamente.
    """
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
        logger.info(f"Diretório de dados criado: {DATA_DIR}")


def init_db() -> None:
    """
    Inicializa o banco de dados com a tabela necessária.

    Cria a tabela de pontos de escavação se não existir, definindo
    a estrutura adequada para armazenar todos os atributos necessários.
    """
    ensure_data_dir()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(f'''
    CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
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


def create_point(point: 'ExcavationPoint') -> int:
    """
    Cria um novo ponto de escavação no banco de dados.

    Args:
        point: Objeto ExcavationPoint contendo os dados do ponto a ser criado.

    Returns:
        int: ID do ponto criado.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        f'''
        INSERT INTO {TABLE_NAME} 
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


def get_all_points() -> pd.DataFrame:
    """
    Busca todos os pontos de escavação no banco de dados.

    Returns:
        pandas.DataFrame: DataFrame contendo todos os pontos de escavação.
    """
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query(f"SELECT * FROM {TABLE_NAME}", conn)
    conn.close()
    logger.info(f"Consultados {len(df)} pontos do banco de dados")
    return df


def get_point_by_id(point_id: int) -> Optional['ExcavationPoint']:
    """
    Busca um ponto específico pelo ID.

    Args:
        point_id: ID do ponto a ser recuperado.

    Returns:
        ExcavationPoint: Objeto com os dados do ponto encontrado ou None se não existir.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(f"SELECT * FROM {TABLE_NAME} WHERE id = ?", (point_id,))
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


def update_point(point: 'ExcavationPoint') -> bool:
    """
    Atualiza um ponto de escavação existente.

    Args:
        point: Objeto ExcavationPoint com os dados atualizados e ID válido.

    Returns:
        bool: True se a atualização foi bem-sucedida, False caso contrário.

    Raises:
        ValueError: Se o ID do ponto não for especificado.
    """
    if point.id is None:  # Verificação explícita contra None
        logger.error("Tentativa de atualização sem ID")
        raise ValueError("ID de ponto não especificado para atualização")
    
    # Assegura que point.id é int
    point_id = int(point.id)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Primeiro verificamos se o ponto existe
    cursor.execute(f"SELECT id FROM {TABLE_NAME} WHERE id = ?", (point_id,))
    if not cursor.fetchone():
        conn.close()
        logger.warning(f"Tentativa de atualizar ponto inexistente com ID: {point_id}")
        return False

    cursor.execute(
        f'''
        UPDATE {TABLE_NAME} 
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
            point_id
        )
    )

    conn.commit()
    updated = cursor.rowcount > 0
    conn.close()

    if updated:
        logger.info(f"Ponto atualizado com ID: {point_id}")
    else:
        logger.warning(f"Falha ao atualizar ponto com ID: {point_id}")

    return updated


def delete_point(point_id: int) -> bool:
    """
    Remove um ponto de escavação pelo ID.

    Args:
        point_id: ID do ponto a ser removido.

    Returns:
        bool: True se a exclusão foi bem-sucedida, False caso contrário.
    """
    logger.info(f"Tentando excluir ponto com ID: {point_id}")

    try:
        # Conecta ao banco de dados com pragma de isolation_level None para auto-commit
        conn = sqlite3.connect(DB_PATH, isolation_level=None)
        cursor = conn.cursor()

        # Verifica se o ponto existe
        cursor.execute(f"SELECT COUNT(*) FROM {TABLE_NAME} WHERE id = ?", (point_id,))
        count = cursor.fetchone()[0]

        if count == 0:
            logger.warning(f"Ponto com ID {point_id} não existe para exclusão")
            conn.close()
            return False

        # Log para ajudar a debug
        logger.info(f"Encontrado ponto com ID {point_id} para exclusão")

        # Executa a exclusão diretamente
        cursor.execute(f"DELETE FROM {TABLE_NAME} WHERE id = ?", (point_id,))

        # Forçar commit (embora isolation_level=None já faça isso)
        conn.commit()

        # Verifica se a exclusão foi bem-sucedida
        cursor.execute(f"SELECT COUNT(*) FROM {TABLE_NAME} WHERE id = ?", (point_id,))
        remaining = cursor.fetchone()[0]

        # Fecha a conexão
        conn.close()

        if remaining == 0:
            logger.info(f"Ponto com ID {point_id} excluído com sucesso")
            return True
        else:
            logger.error(f"Falha ao excluir: ponto com ID {point_id} ainda existe")
            return False

    except Exception as e:
        logger.error(f"Erro ao excluir ponto com ID {point_id}: {str(e)}")
        # Tenta fechar a conexão se ainda estiver aberta
        try:
            if 'conn' in locals() and conn:
                conn.close()
        except:
            pass
        return False


def search_points(query: str = "", field: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Busca pontos de escavação com base em um termo de pesquisa.

    Args:
        query: Termo de pesquisa a ser buscado nos campos.
        field: Campo específico para limitar a busca (opcional).

    Returns:
        list: Lista de dicionários contendo os pontos encontrados.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        if field and query:
            sql_query = f"SELECT * FROM {TABLE_NAME} WHERE {field} LIKE ?"
            cursor.execute(sql_query, (f"%{query}%",))
        elif query:
            sql_query = f"SELECT * FROM {TABLE_NAME} WHERE point_type LIKE ? OR description LIKE ? OR responsible LIKE ?"
            cursor.execute(sql_query, (f"%{query}%", f"%{query}%", f"%{query}%",))
        else:
            cursor.execute(f"SELECT * FROM {TABLE_NAME}")

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
