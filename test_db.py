from connect_db import get_db_connection, return_db_connection

conn = get_db_connection()
if conn:
    print("¡Conexión exitosa!")
    cursor = conn.cursor()
    cursor.execute("SELECT version();")
    print("Versión de PostgreSQL:", cursor.fetchone())
    return_db_connection(conn)
else:
    print("No se pudo conectar a la base de datos.")