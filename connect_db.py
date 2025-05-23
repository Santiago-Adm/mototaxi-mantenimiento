import os
import psycopg2
from psycopg2 import pool, OperationalError
import logging

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_db_config():
    """Configuración segura con manejo de errores"""
    try:
        return {
            "host": os.environ['POSTGRES_HOST'],
            "database": os.environ['POSTGRES_DB'],
            "user": f"{os.environ['POSTGRES_USER']}@odernando-ase14",
            "password": os.environ['POSTGRES_PASSWORD'],
            "port": os.environ.get('POSTGRES_PORT', '5432'),
            "sslmode": "require",
            "connect_timeout": 10,
            "keepalives": 1,
            "keepalives_idle": 30,
            "keepalives_interval": 10,
            "keepalives_count": 5
        }
    except KeyError as e:
        logger.error(f"Variable de entorno faltante: {e}")
        raise

# Pool de conexiones global
connection_pool = None

def init_db_pool():
    """Inicialización robusta del pool"""
    global connection_pool
    try:
        db_config = get_db_config()
        connection_pool = psycopg2.pool.ThreadedConnectionPool(
            minconn=1,
            maxconn=5,
            **db_config
        )
        logger.info("Pool de conexiones inicializado correctamente")
    except OperationalError as e:
        logger.error(f"Error de conexión: {e}")
        connection_pool = None

def get_db_connection():
    """Obtiene conexión con verificación activa"""
    global connection_pool
    if not connection_pool:
        init_db_pool()
    
    try:
        conn = connection_pool.getconn()
        # Verificación de conexión activa
        with conn.cursor() as cur:
            cur.execute("SELECT 1")
        return conn
    except Exception as e:
        logger.error(f"Error al obtener conexión: {e}")
        return None

def return_db_connection(conn):
    """Devuelve conexión de forma segura"""
    if conn and connection_pool:
        try:
            if not conn.closed:
                conn.rollback()
            connection_pool.putconn(conn)
        except Exception as e:
            logger.error(f"Error al devolver conexión: {e}")

# Inicialización al importar
init_db_pool()