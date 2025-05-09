from flask import Flask, request, jsonify, render_template
import pyodbc
from azure.identity import DefaultAzureCredential
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

app = Flask(__name__)

# Configuración de la conexión a Azure SQL Database
server = os.getenv('AZURE_SQL_SERVER')
database = os.getenv('AZURE_SQL_DATABASE')
username = os.getenv('AZURE_SQL_USERNAME')
password = os.getenv('AZURE_SQL_PASSWORD')
driver = '{ODBC Driver 18 for SQL Server}'

# Cadena de conexión
connection_string = f'DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}'

# Endpoint para la página principal
@app.route('/')
def index():
    return render_template('index.html')

# Endpoint para agregar un vehículo
@app.route('/api/vehicles', methods=['POST'])
def add_vehicle():
    try:
        data = request.get_json()
        license_plate = data['license_plate']
        owner_name = data['owner_name']
        model = data['model']
        
        with pyodbc.connect(connection_string) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO Vehicles (LicensePlate, OwnerName, Model) VALUES (?, ?, ?)",
                (license_plate, owner_name, model)
            )
            conn.commit()
        return jsonify({'message': 'Vehículo agregado exitosamente'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Endpoint para listar vehículos
@app.route('/api/vehicles', methods=['GET'])
def get_vehicles():
    try:
        with pyodbc.connect(connection_string) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Vehicles")
            rows = cursor.fetchall()
            vehicles = [
                {'id': row[0], 'license_plate': row[1], 'owner_name': row[2], 'model': row[3]}
                for row in rows
            ]
        return jsonify(vehicles), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)