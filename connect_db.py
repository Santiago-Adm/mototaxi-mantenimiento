import psycopg2
from psycopg2 import pool

# Configuración para Azure PostgreSQL
azure_db_params = {
    "host": "mototaxi-aplication.postgres.database.azure.com",
    "database": "postgres",
    "user": "kkecjzsbkx",
    "password": "contraseña_segura_12",
    "port": "5432",
    "sslmode": "require"
}

# Pool de conexiones
try:
    connection_pool = psycopg2.pool.SimpleConnectionPool(
        minconn=1,
        maxconn=10,
        **azure_db_params
    )
    print("Pool de conexiones creado correctamente.")
except psycopg2.Error as e:
    print(f"Error al crear el pool: {e}")

# Funciones (nivel raíz, sin indentación extra)
def get_db_connection():
    try:
        return connection_pool.getconn()
    except psycopg2.Error as e:
        print(f"Error al obtener conexión: {e}")
        return None

def return_db_connection(conn):
    if conn:
        connection_pool.putconn(conn)