import psycopg2

try:
    cnx = psycopg2.connect(
        user="yxascysndu@mototaxi-aplication-01-server",  # Formato usuario@servidor
        password="MiContraseña123",  # Tu contraseña
        host="mototaxi-aplication-01-server.postgres.database.azure.com",
        port=5432,
        database="mototaxi-aplication-01-database",  # Nombre de la base de datos
        sslmode="require"  # Requerido por Azure
    )
    print("Conexión exitosa!")
    cnx.close()
except psycopg2.Error as e:
    print(f"Error al conectar: {e}")