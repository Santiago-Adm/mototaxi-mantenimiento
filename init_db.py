import psycopg2
from dotenv import load_dotenv
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

def init_database():
    try:
        logger.info("Starting database initialization...")
        
        # Log connection parameters (without password)
        logger.info(f"Connecting to: {os.getenv('POSTGRES_HOST')}")
        logger.info(f"Database: {os.getenv('POSTGRES_DB')}")
        logger.info(f"User: {os.getenv('POSTGRES_USER')}")
        
        # Construct connection string
        conn_string = (
            f"host={os.getenv('POSTGRES_HOST')} "
            f"dbname={os.getenv('POSTGRES_DB')} "
            f"user={os.getenv('POSTGRES_USER')} "  # Remove @motitodatabase from here
            f"password={os.getenv('POSTGRES_PASSWORD')} "
            f"port={os.getenv('POSTGRES_PORT')} "
            "sslmode=require"
        )
        
        # Connect to database
        logger.info("Attempting to connect to database...")
        conn = psycopg2.connect(conn_string)
        cur = conn.cursor()
        
        # Create tables
        logger.info("Creating tables...")
        cur.execute("""
            CREATE TABLE IF NOT EXISTS usuario (
                id SERIAL PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                email VARCHAR(120) UNIQUE NOT NULL
            )
        """)
        
        cur.execute("""
            CREATE TABLE IF NOT EXISTS vehiculos (
                id SERIAL PRIMARY KEY,
                last_names VARCHAR(100) NOT NULL,
                first_names VARCHAR(100) NOT NULL,
                dni VARCHAR(20) UNIQUE NOT NULL,
                license_plate VARCHAR(20) UNIQUE NOT NULL,
                model VARCHAR(50) NOT NULL
            )
        """)
        
        # Commit changes
        conn.commit()
        logger.info("Database tables created successfully")
        
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        raise
    finally:
        if 'cur' in locals():
            cur.close()
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    init_database()