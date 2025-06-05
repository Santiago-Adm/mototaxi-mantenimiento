from flask import Flask, request, jsonify, render_template, session, redirect, url_for
from werkzeug.security import check_password_hash, generate_password_hash
import psycopg2
import os
from dotenv import load_dotenv
import psycopg2.extras
from functools import wraps
import logging

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
        # Log connection attempt
        logger.info(f"Attempting to connect to {os.getenv('POSTGRES_HOST')}")
        
        conn_string = (
            f"host={os.getenv('POSTGRES_HOST')} "
            f"dbname={os.getenv('POSTGRES_DB')} "
            f"user={os.getenv('POSTGRES_USER')}@motitodatabase "  # Add server name after @
            f"password={os.getenv('POSTGRES_PASSWORD')} "
            f"port={os.getenv('POSTGRES_PORT')} "
            "sslmode=require"
        )
        conn = psycopg2.connect(conn_string)
        logger.info("Database connection successful")
        return conn
    except Exception as e:
        logger.error(f"Database connection error: {e}")
        return None

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

        with get_db_connection() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute("SELECT * FROM usuario WHERE username = %s", (username,))
                user = cur.fetchone()

                if user and check_password_hash(user['password_hash'], password):
                    session['user_id'] = user['id']
                    session['username'] = user['username']
                    return jsonify({"message": "Login exitoso"}), 200
                
                return jsonify({"error": "Usuario o contraseña incorrectos"}), 401

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
        if conn:
            with conn.cursor() as cur:
                cur.execute('SELECT 1')
                result = cur.fetchone()
                conn.close()
                return jsonify({
                    "status": "success",
                    "message": "Conexión exitosa a la base de datos",
                    "result": result[0]
                })
        return jsonify({
            "status": "error",
            "message": "No se pudo establecer la conexión"
        }), 500
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

if __name__ == '__main__':
    port = int(os.environ.get('WEBSITES_PORT', 8000))
    app.run(host='0.0.0.0', port=port)
