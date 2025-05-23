import psycopg2
from psycopg2 import pool, OperationalError
import os
from dotenv import load_dotenv
import ssl

# Cargar variables de entorno
load_dotenv()

class DatabaseConfig:
    @staticmethod
    def get_ssl_context():
        """Configura el contexto SSL para Azure PostgreSQL"""
        ssl_context = ssl.create_default_context()
        ssl_context.verify_mode = ssl.CERT_REQUIRED
        ssl_context.check_hostname = True
        return ssl_context

    @staticmethod
    def get_db_config():
        """Configuración dinámica para VNet o acceso público"""
        config = {
            "host": os.getenv('POSTGRES_PRIVATE_HOST') if os.getenv('USE_PRIVATE_ENDPOINT') == 'true' 
                   else os.getenv('POSTGRES_HOST'),
            "database": os.getenv('POSTGRES_DB'),
            "user": f"{os.getenv('POSTGRES_USER')}@odernando-ase14",  # Formato requerido por Azure
            "password": os.getenv('POSTGRES_PASSWORD'),
            "port": os.getenv('POSTGRES_PORT'),
            "sslmode": "require",
            "sslrootcert": os.path.join(os.path.dirname(__file__), 'BaltimoreCyberTrustRoot.crt.pem'),
            "connect_timeout": 10,
            "keepalives": 1,
            "keepalives_idle": 60,
            "keepalives_interval": 15,
            "keepalives_count": 5,
            "options": f"-c search_path=public"  # Esquema por defecto
        }
        return {k: v for k, v in config.items() if v is not None}

# Pool de conexiones global
connection_pool = None

def init_db_pool():
    """Inicialización segura del pool de conexiones"""
    global connection_pool
    try:
        db_config = DatabaseConfig.get_db_config()
        connection_pool = psycopg2.pool.ThreadedConnectionPool(
            minconn=2,
            maxconn=15,  # Ajustado para tu plan B2ms
            **db_config
        )
        print("✅ Pool configurado para odernando-ase14 (Canada Central)")
    except Exception as e:
        print(f"❌ Error inicializando pool: {str(e)}")
        connection_pool = None

def get_db_connection():
    """Obtiene conexión con manejo de errores mejorado"""
    if not connection_pool:
        init_db_pool()
    
    try:
        conn = connection_pool.getconn()
        conn.autocommit = False
        # Test connection
        with conn.cursor() as cur:
            cur.execute("SELECT 1")
        return conn
    except OperationalError as e:
        print(f"⚠️ Error de conexión: {e}. Reintentando...")
        init_db_pool()  # Reintentar
        return connection_pool.getconn() if connection_pool else None
    except Exception as e:
        print(f"⚠️ Error inesperado: {e}")
        return None

def return_db_connection(conn):
    """Devuelve conexión de forma segura"""
    if conn and connection_pool:
        try:
            if not conn.closed:
                conn.rollback()
            connection_pool.putconn(conn)
        except Exception as e:
            print(f"⚠️ Error devolviendo conexión: {e}")
            try:
                conn.close()
            except:
                pass

class DBConnection:
    """Context manager para manejo automático"""
    def __enter__(self):
        self.conn = get_db_connection()
        if not self.conn:
            raise ConnectionError("No se pudo establecer conexión con la base de datos")
        return self.conn
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.conn:
            if exc_type:
                self.conn.rollback()
            return_db_connection(self.conn)

# Inicialización al importar
init_db_pool()