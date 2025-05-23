import os
import psycopg2
from psycopg2 import pool, OperationalError
import logging

from app import get_db_connection

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
def get_db_config():
    """Configuración única para Private Endpoint"""
    return {
        "host": os.getenv('POSTGRES_HOST'),
        "database": os.getenv('POSTGRES_DB'),
        "user": os.getenv('POSTGRES_USER'),  # Ya incluye @servidor
        "password": os.getenv('POSTGRES_PASSWORD'),
        "port": os.getenv('POSTGRES_PORT'),
        "sslmode": os.getenv('POSTGRES_SSL'),
        "connect_timeout": 10
    }

def return_db_connection(conn):
    """Devuelve conexión de forma segura"""
    if conn:
        try:
            if not conn.closed:
                conn.rollback()
            conn.close()
        except Exception as e:
            logger.error(f"Error al cerrar conexión: {e}")