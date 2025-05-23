import os
import psycopg2
from psycopg2 import pool, OperationalError
import logging

# Configura logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DBConnection:
    """Context manager para manejo de conexiones"""
    def __init__(self):
        self.conn = None

    def __enter__(self):
        try:
            self.conn = get_db_connection()
            if not self.conn:
                raise ConnectionError("No se pudo establecer conexión con la base de datos")
            return self.conn
        except Exception as e:
            logger.error(f"Error al obtener conexión: {e}")
            raise

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.conn:
            try:
                if exc_type:  # Hubo un error
                    self.conn.rollback()
                return_db_connection(self.conn)
            except Exception as e:
                logger.error(f"Error al devolver conexión: {e}")

# Resto de tus funciones (get_db_connection, return_db_connection, etc.)
def get_db_connection():
    """Obtiene conexión del pool"""
    try:
        conn = psycopg2.connect(
            host=os.getenv('POSTGRES_HOST'),
            database=os.getenv('POSTGRES_DB'),
            user=f"{os.getenv('POSTGRES_USER')}@{os.getenv('POSTGRES_HOST').split('.')[0]}",
            password=os.getenv('POSTGRES_PASSWORD'),
            port=os.getenv('POSTGRES_PORT', '5432'),
            sslmode='require'
        )
        return conn
    except OperationalError as e:
        logger.error(f"Error de conexión: {e}")
        return None

def return_db_connection(conn):
    """Devuelve conexión de forma segura"""
    if conn:
        try:
            if not conn.closed:
                conn.rollback()
            conn.close()
        except Exception as e:
            logger.error(f"Error al cerrar conexión: {e}")