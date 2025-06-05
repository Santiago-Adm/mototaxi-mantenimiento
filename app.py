from flask import Flask, request, jsonify, render_template, session, redirect, url_for
from werkzeug.security import check_password_hash, generate_password_hash
import psycopg2
import os
from dotenv import load_dotenv
import psycopg2.extras
from functools import wraps
import logging
import pyodbc  # Add this import at the top

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')

# Azure-specific configurations
app.config.update(
    SESSION_COOKIE_SECURE=True,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax'
)

def get_db_connection():
    try:
        logger.info("Attempting to connect to database...")
        
        conn_string = os.getenv('SQL_CONNECTION_STRING')
        
        # Add default connection timeout and configure retry logic
        if "Connection Timeout=" not in conn_string:
            conn_string += ";Connection Timeout=30"
        if "ConnectRetryCount=" not in conn_string:
            conn_string += ";ConnectRetryCount=3;ConnectRetryInterval=10"
        
        # Add driver if not present
        if "Driver=" not in conn_string:
            conn_string = "Driver={ODBC Driver 17 for SQL Server};" + conn_string
        
        # Create connection using pyodbc
        conn = pyodbc.connect(conn_string)
        conn.timeout = 30  # Set command timeout
        
        # Test connection
        with conn.cursor() as cur:
            cur.execute('SELECT 1')
            cur.fetchone()
        
        logger.info("Database connection successful")
        return conn
    except pyodbc.Error as e:
        logger.error(f"Database connection error: {e}")
        raise  # Raise the error instead of returning None
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise  # Raise the error instead of returning None

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login_page'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    return redirect(url_for('login_page'))

@app.route('/login')
def login_page():
    if 'user_id' in session:
        return redirect(url_for('mostrar_vehiculos'))
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login_page'))

@app.route('/registro')
def registro_page():
    return render_template('registro.html')

@app.route('/mostrar-vehiculos')
@login_required
def mostrar_vehiculos():
    return render_template('mostrar_vehiculos.html')

@app.route('/api/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            return jsonify({"error": "Usuario y contraseña son requeridos"}), 400

        conn = get_db_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM usuario WHERE username = ?", (username,))
                user = cur.fetchone()

                if user and check_password_hash(user.password_hash, password):
                    session['user_id'] = user.id
                    session['username'] = user.username
                    return jsonify({"message": "Login exitoso"}), 200
                
                return jsonify({"error": "Usuario o contraseña incorrectos"}), 401
        finally:
            if conn:
                conn.close()

    except pyodbc.Error as e:
        logger.error(f"Database error: {str(e)}")
        return jsonify({"error": "Error de conexión con la base de datos"}), 503
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        return jsonify({"error": "Error interno del servidor"}), 500

@app.route('/api/registro', methods=['POST'])
def registro():
    try:
        data = request.get_json()
        password_hash = generate_password_hash(data['password'])
        
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO usuario (username, password_hash, email)
                    VALUES (%s, %s, %s)
                    RETURNING id
                """, (data['username'], password_hash, data['email']))
                user_id = cur.fetchone()[0]

                # Registro del vehículo si se proporcionan los datos
                if 'vehicle' in data:
                    vehicle = data['vehicle']
                    cur.execute("""
                        INSERT INTO vehiculos (last_names, first_names, dni, license_plate, model)
                        VALUES (%s, %s, %s, %s, %s)
                        RETURNING id
                    """, (vehicle['last_names'], vehicle['first_names'], 
                          vehicle['dni'], vehicle['license_plate'], vehicle['model']))
                    vehicle_id = cur.fetchone()[0]
                
                conn.commit()
                return jsonify({
                    "message": "Registro exitoso",
                    "id": user_id
                }), 201
                
    except psycopg2.IntegrityError:
        return jsonify({"error": "El usuario o email ya existe"}), 409
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/vehicles', methods=['GET'])
def get_vehicles():
    try:
        with get_db_connection() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute("""
                    SELECT id, last_names, first_names, dni, license_plate, model 
                    FROM vehiculos 
                    ORDER BY id DESC
                """)
                vehicles = cur.fetchall()
                return jsonify(vehicles)
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/test-db')
def test_db():
    try:
        conn = get_db_connection()
        if conn:
            conn.close()
            return jsonify({"status": "success", "message": "Database connection successful"})
        return jsonify({"status": "error", "message": "Could not establish database connection"}), 500
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/test-connection')
def test_connection():
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute('SELECT @@version')
            version = cursor.fetchone()[0]
        return jsonify({
            "status": "success",
            "message": "Conexión exitosa a la base de datos",
            "version": version
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

if __name__ == '__main__':
    port = int(os.environ.get('WEBSITES_PORT', 8000))
    app.run(host='0.0.0.0', port=port)
