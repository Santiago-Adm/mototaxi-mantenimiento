from flask import Flask, request, jsonify, render_template
import psycopg2
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

app = Flask(__name__)

# Configuración de la conexión a Azure PostgreSQL
db_params = {
    'dbname': os.getenv('POSTGRES_DB'),
    'user': os.getenv('POSTGRES_USER'),
    'password': os.getenv('POSTGRES_PASSWORD'),
    'host': os.getenv('POSTGRES_HOST'),
    'port': os.getenv('POSTGRES_PORT', '5432'),
    'sslmode': 'require'
}

# Endpoint para la página principal (solo formulario)
@app.route('/')
def index():
    return render_template('index.html')

# Nueva ruta para la página de login
@app.route('/login')
def login():
    return render_template('login.html', page_class='login-page')

# Nueva ruta para mostrar vehículos
@app.route('/mostrar-vehiculos')
def mostrar_vehiculos():
    return render_template('mostrar_vehiculos.html')

# Endpoint para agregar un vehículo
@app.route('/api/vehicles', methods=['POST'])
def add_vehicle():
    try:
        data = request.get_json()
        last_names = data['last_names']
        first_names = data['first_names']
        dni = data['dni']
        license_plate = data['license_plate']
        model = data['model']
        
        # Conexión a PostgreSQL
        conn = psycopg2.connect(**db_params)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO Vehiculos (last_names, first_names, dni, license_plate, model) VALUES (%s, %s, %s, %s, %s)",
            (last_names, first_names, dni, license_plate, model)
        )
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({'message': 'Vehículo agregado exitosamente'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Endpoint para listar vehículos
@app.route('/api/vehicles', methods=['GET'])
def get_vehicles():
    try:
        # Conexión a PostgreSQL
        conn = psycopg2.connect(**db_params)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Vehiculos")
        rows = cursor.fetchall()
        vehicles = [
            {
                'id': row[0],
                'last_names': row[1],
                'first_names': row[2],
                'dni': row[3],
                'license_plate': row[4],
                'model': row[5]
            }
            for row in rows
        ]
        cursor.close()
        conn.close()
        return jsonify(vehicles), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)