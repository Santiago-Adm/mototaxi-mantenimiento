import os
import psycopg2
from psycopg2 import pool

def get_db_config():
    return {
        "host": os.getenv('POSTGRES_HOST'),
        "database": os.getenv('POSTGRES_DB'),
        "user": os.getenv('POSTGRES_USER'),
        "password": os.getenv('POSTGRES_PASSWORD'),
        "port": os.getenv('POSTGRES_PORT'),
        "sslmode": os.getenv('POSTGRES_SSL')
    }

# Pool de conexiones simple
try:
    connection_pool = psycopg2.pool.SimpleConnectionPool(
        minconn=1,
        maxconn=5,  # Adecuado para plan B1
        **get_db_config()
    )
except Exception as e:
    print(f"Error al crear pool: {e}")
    connection_pool = None

def get_db_connection():
    if connection_pool:
        return connection_pool.getconn()
    return None

def return_db_connection(conn):
    if conn and connection_pool:
        connection_pool.putconn(conn)