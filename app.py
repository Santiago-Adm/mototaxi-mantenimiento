from flask import Flask, request, jsonify, render_template
import psycopg2
import os
from dotenv import load_dotenv
from connect_db import DBConnection
import time

# Cargar variables de entorno
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))
print("Archivo .env cargado:", os.path.exists(os.path.join(os.path.dirname(__file__), '.env')))
print("POSTGRES_HOST:", os.getenv('POSTGRES_HOST'))
print("POSTGRES_USER:", os.getenv('POSTGRES_USER'))
print("POSTGRES_PASSWORD:", os.getenv('POSTGRES_PASSWORD'))
print("POSTGRES_DB:", os.getenv('POSTGRES_DB'))
print("POSTGRES_PORT:", os.getenv('POSTGRES_PORT'))

app = Flask(__name__)

# Configuración de la conexión a PostgreSQL
db_params = {
    'host': os.getenv('POSTGRES_HOST', 'localhost'),
    'user': os.getenv('POSTGRES_USER', 'postgres'),
    'password': os.getenv('POSTGRES_PASSWORD'),
    'dbname': os.getenv('POSTGRES_DB', 'vehiculos_db'),
    'port': os.getenv('POSTGRES_PORT', '5432')
}

# Modifica get_db_connection() en app.py
def get_db_connection():
    conn = psycopg2.connect(
        host=os.getenv('POSTGRES_HOST'),
        user=os.getenv('POSTGRES_USER'),
        password=os.getenv('POSTGRES_PASSWORD'),
        dbname=os.getenv('POSTGRES_DB'),
        port=os.getenv('POSTGRES_PORT'),
        sslmode='require',
        connect_timeout=10  # Añade timeout explícito
    )
    return conn

@app.route('/test-connection')
def test_connection():
    try:
        with DBConnection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT version()")
                version = cur.fetchone()
        return f"PostgreSQL {version[0]}", 200
    except Exception as e:
        return f"Error: {str(e)}", 500

@app.route('/test-db')
def test_db():
    try:
        conn = get_db_connection()
        if conn:
            with conn.cursor() as cur:
                cur.execute("SELECT version()")
                version = cur.fetchone()
            return f"PostgreSQL {version[0]}", 200
        return "No hay conexión a la DB", 500
    except Exception as e:
        return f"Error: {str(e)}", 500
    
@app.route('/db-status')
def db_status():
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT version()")
                version = cur.fetchone()
        return f"PostgreSQL {version[0]}", 200
    except Exception as e:
        return f"Error: {str(e)}", 500
    
@app.route('/db-check')
def db_check():
    try:
        start_time = time.time()
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT version()")
                version = cur.fetchone()
                cur.execute("SELECT COUNT(*) FROM vehiculos")  # Ajusta según tu esquema
                count = cur.fetchone()
        return jsonify({
            "status": "success",
            "postgres_version": version[0],
            "row_count": count[0],
            "response_time": f"{(time.time() - start_time):.2f}s"
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login')
def login_page():
    return render_template('login.html', page_class='login-page')

@app.route('/mostrar-vehiculos')
def mostrar_vehiculos():
    return render_template('mostrar_vehiculos.html')

@app.route('/api/vehicles', methods=['POST'])
def add_vehicle():
    try:
        data = request.get_json()
        if not all(k in data for k in ['last_names', 'first_names', 'dni', 'license_plate', 'model']):
            return jsonify({'error': 'Faltan campos requeridos'}), 400
        
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                # Insertar vehículo
                cursor.execute(
                    "INSERT INTO Vehiculos (last_names, first_names, dni, license_plate, model) VALUES (%s, %s, %s, %s, %s) RETURNING id",
                    (data['last_names'], data['first_names'], data['dni'], data['license_plate'], data['model'])
                )
                vehicle_id = cursor.fetchone()[0]
                
                # Crear usuario automático
                username = f"{data['first_names'].lower().split()[0]}{data['dni'][-4:]}"
                password = data['license_plate'].lower().replace("-", "")
                email = f"{username}@mototaxi.com"  # Email ficticio
                
                # Insertar usuario (password_hash es igual al password en texto plano por simplicidad)
                cursor.execute(
                    "INSERT INTO usuario (username, password_hash, email) VALUES (%s, %s, %s)",
                    (username, password, email)  # En producción deberías hashear la contraseña
                )
                
                conn.commit()
                
        return jsonify({
            'message': 'Vehículo agregado exitosamente',
            'credentials': {
                'username': username,
                'password': password
            }
        }), 201
        
    except psycopg2.Error as e:
        return jsonify({'error': f'Error de base de datos: {str(e)}'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/vehicles', methods=['GET'])
def get_vehicles():
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM Vehiculos")
                rows = cursor.fetchall()
                vehicles = [
                    {'id': row[0], 'last_names': row[1], 'first_names': row[2], 'dni': row[3],
                     'license_plate': row[4], 'model': row[5]}
                    for row in rows
                ]
        return jsonify(vehicles), 200
    except psycopg2.Error as e:
        return jsonify({'error': f'Error de base de datos: {str(e)}'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)

@app.route('/api/login', methods=['POST'])
def api_login():  # ¡Nombre diferente a la ruta /login!
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Datos no proporcionados'}), 400
            
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({'error': 'Usuario y contraseña requeridos'}), 400
            
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "SELECT id FROM usuario WHERE username = %s AND password_hash = %s",
                    (username, password)
                )
                user = cursor.fetchone()
                
                if user:
                    return jsonify({'message': 'Autenticación exitosa'}), 200
                else:
                    return jsonify({'error': 'Credenciales inválidas'}), 401
                    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
    response.headers.add('Access-Control-Allow-Methods', 'POST')
    return response