import pyodbc
from dotenv import load_dotenv
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

def test_connection():
    try:
        logger.info("Testing database connection...")
        
        # Get connection string
        conn_string = os.getenv('SQL_CONNECTION_STRING')
        
        # List available drivers
        logger.info("Available ODBC drivers:")
        for driver in pyodbc.drivers():
            logger.info(f"  - {driver}")
            
        # Add driver specification to connection string if not present
        if "Driver=" not in conn_string:
            conn_string = "Driver={ODBC Driver 17 for SQL Server};" + conn_string
            
        logger.info("Attempting connection with modified string...")
        
        # Connect to database
        conn = pyodbc.connect(conn_string)
        
        # Test query
        with conn.cursor() as cursor:
            cursor.execute('SELECT @@VERSION')
            row = cursor.fetchone()
            logger.info(f"SQL Server Version: {row[0]}")
            
        logger.info("Connection test successful!")
        conn.close()
        
    except Exception as e:
        logger.error(f"Connection test failed: {e}")
        logger.error("Full connection string (with password hidden):")
        # Safely log connection string by hiding password
        safe_conn_string = conn_string.replace(os.getenv('SQL_PASSWORD', ''), '***')
        logger.error(safe_conn_string)

if __name__ == "__main__":
    test_connection()