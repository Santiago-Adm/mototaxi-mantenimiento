from flask import Flask, request, jsonify, render_template
import psycopg2
import os
from dotenv import load_dotenv

# Cargar variables de entorno (opcional localmente, no en producción)
load_dotenv()  # Esto solo se usa si pruebas localmente

app = Flask(__name__)

# Configuración de la conexión a Azure PostgreSQL
db_params = {
    'dbname': os.getenv('POSTGRES_DB', 'mototaxi-application-01-database'),
    'user': os.getenv('POSTGRES_USER', 'yxascysndu@mototaxi-aplication-01-server'),
    'password': os.getenv('POSTGRES_PASSWORD', 'clFcM$u4V2RtI$t$k'),
    'host': os.getenv('POSTGRES_HOST', 'mototaxi-aplication-01-server.postgres.database.azure.com'),
    'port': os.getenv('POSTGRES_PORT', '5432'),
    'sslmode': 'require'
}

def get_db_connection():
    return psycopg2.connect(**db_params)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login')
def login():
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
                cursor.execute(
                    "INSERT INTO Vehiculos (last_names, first_names, dni, license_plate, model) VALUES (%s, %s, %s, %s, %s)",
                    (data['last_names'], data['first_names'], data['dni'], data['license_plate'], data['model'])
                )
                conn.commit()
        return jsonify({'message': 'Vehículo agregado exitosamente'}), 201
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