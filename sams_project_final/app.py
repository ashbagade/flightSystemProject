from flask import Flask, render_template, request, redirect, url_for, flash, g, jsonify
from flask_bootstrap import Bootstrap5
import mysql.connector
from dotenv import load_dotenv
import os
import logging

# Load environment variables from the correct path
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__, 
           template_folder='frontend/templates',
           static_folder='frontend/static')
app.secret_key = os.getenv('SECRET_KEY', 'dev')  # Change this in production
bootstrap = Bootstrap5(app)

# Database configuration
db_config = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', ''),
    'database': os.getenv('DB_NAME', 'flight_tracking')
}

def get_db_connection():
    try:
        if 'db' not in g:
            g.db = mysql.connector.connect(**db_config)
            logger.info("Database connection established successfully")
        return g.db
    except mysql.connector.Error as err:
        logger.error(f"Database connection error: {err}")
        raise

@app.teardown_appcontext
def close_db(error):
    db = g.pop('db', None)
    if db is not None:
        db.close()
        logger.info("Database connection closed")

@app.errorhandler(404)
def not_found_error(error):
    logger.error(f"404 error: {error}")
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"500 error: {error}")
    return render_template('500.html'), 500

@app.route('/health')
def health_check():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT 1')
        cursor.fetchone()
        cursor.close()
        return jsonify({'status': 'healthy', 'database': 'connected'})
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({'status': 'unhealthy', 'error': str(e)}), 500

@app.route('/')
def index():
    try:
        return render_template('index.html')
    except Exception as e:
        logger.error(f"Error in index route: {e}")
        flash('An error occurred while loading the page', 'error')
        return render_template('index.html')

@app.route('/flights')
def flights():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Get both in-air and on-ground flights
        cursor.execute('SELECT * FROM flights_in_the_air')
        flights_air = cursor.fetchall()
        logger.debug(f"Found {len(flights_air)} flights in the air")
        
        cursor.execute('SELECT * FROM flights_on_the_ground')
        flights_ground = cursor.fetchall()
        logger.debug(f"Found {len(flights_ground)} flights on the ground")
        
        cursor.close()
        return render_template('flights.html', flights_air=flights_air, flights_ground=flights_ground)
    except mysql.connector.Error as err:
        logger.error(f"Database error in flights route: {err}")
        flash(f"Database error: {err}", 'error')
        return render_template('flights.html', flights_air=[], flights_ground=[])
    except Exception as e:
        logger.error(f"Unexpected error in flights route: {e}")
        flash(f"An unexpected error occurred: {e}", 'error')
        return render_template('flights.html', flights_air=[], flights_ground=[])

@app.route('/people')
def people():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Get both in-air and on-ground people
        cursor.execute('SELECT * FROM people_in_the_air')
        people_air = cursor.fetchall()
        logger.debug(f"Found {len(people_air)} people in the air")
        
        cursor.execute('SELECT * FROM people_on_the_ground')
        people_ground = cursor.fetchall()
        logger.debug(f"Found {len(people_ground)} people on the ground")
        
        cursor.close()
        return render_template('people.html', people_air=people_air, people_ground=people_ground)
    except mysql.connector.Error as err:
        logger.error(f"Database error in people route: {err}")
        flash(f"Database error: {err}", 'error')
        return render_template('people.html', people_air=[], people_ground=[])
    except Exception as e:
        logger.error(f"Unexpected error in people route: {e}")
        flash(f"An unexpected error occurred: {e}", 'error')
        return render_template('people.html', people_air=[], people_ground=[])

@app.route('/add_airplane', methods=['GET', 'POST'])
def add_airplane():
    if request.method == 'POST':
        airline_id = request.form['airline_id']
        tail_num = request.form['tail_num']
        seat_capacity = request.form.get('seat_cap', type=int)
        speed = request.form.get('speed', type=int)
        location_id = request.form['location_id']
        plane_type = request.form['plane_type']
        maintained = request.form.get('maintained')
        model = request.form.get('model')
        neo = request.form.get('neo', 'FALSE')

        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            # Use the stored procedure instead of direct INSERT
            cursor.callproc('add_airplane', (airline_id, tail_num, seat_capacity, speed,
                                           location_id, plane_type, maintained, model, neo))
            conn.commit()
            flash('Airplane added successfully!', 'success')
        except mysql.connector.Error as err:
            flash(f'Error: {err}', 'error')
        finally:
            cursor.close()
            conn.close()
        return redirect(url_for('add_airplane'))
    
    # Get list of airlines for the form
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT airlineID FROM airline')
    airlines = cursor.fetchall()
    cursor.close()
    conn.close()
    
    return render_template('add_airplane.html', airlines=airlines)

@app.route('/add_airport', methods=['GET', 'POST'])
def add_airport():
    if request.method == 'POST':
        airport_id = request.form['airport_id']
        airport_name = request.form.get('airport_name')
        city = request.form['city']
        state = request.form['state']
        country = request.form['country']
        location_id = request.form['location_id']

        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.callproc('add_airport', (airport_id, airport_name, city, state, country, location_id))
            conn.commit()
            flash('Airport added successfully!', 'success')
        except mysql.connector.Error as err:
            flash(f'Error: {err}', 'error')
        finally:
            cursor.close()
            conn.close()
        return redirect(url_for('add_airport'))
    
    return render_template('add_airport.html')

@app.route('/routes')
def routes():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM route_summary')
    routes = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('routes.html', routes=routes)

@app.route('/alternative_airports')
def alternative_airports():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM alternative_airports')
    airports = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('alternative_airports.html', airports=airports)

if __name__ == '__main__':
    app.run(debug=True) 