import psycopg2

try:
    cnx = psycopg2.connect(
        user="yxascysndu@mototaxi-aplication-01-server",
        password="MiContraseña123",  # Reemplaza con tu contraseña
        host="mototaxi-aplication-01-server.postgres.database.azure.com",
        port=5432,
        database="mototaximantenimiento01",
        sslmode="require"
    )
    print("Conexión exitosa!")
    cnx.close()
except psycopg2.Error as e:
    print(f"Error al conectar: {e}")