from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import pymysql
from pymysql.cursors import DictCursor
from config import Config

app = Flask(__name__, 
           template_folder='frontend/templates',
           static_folder='frontend/static')

# Set a secret key for flash messages
app.secret_key = Config.SECRET_KEY

DB_CONFIG = {
    **Config.get_db_config(),
    'cursorclass': DictCursor,
    'port': 3306
}

def get_db_connection():
    """Get a database connection with proper error handling"""
    try:
        conn = pymysql.connect(**DB_CONFIG)
        return conn
    except Exception as e:
        print(f"Database connection error: {str(e)}")
        return None

def handle_db_error(e, operation):
    """Handle database errors and return user-friendly messages"""
    if not hasattr(e, 'args') or len(e.args) == 0:
        return f"Database error during {operation}"
        
    error_code = e.args[0]
    if error_code == 1451:  # Cannot delete or update a parent row (foreign key constraint)
        return "Cannot delete this record because it is being used by other records in the system."
    elif error_code == 1452:  # Cannot add or update a child row (foreign key not found)
        return "Cannot add/update this record because it references a non-existent record."
    elif error_code == 1062:  # Duplicate entry
        return "A record with this ID already exists."
    elif error_code == 1216:  # Cannot add or update a child row (foreign key constraint)
        return "Cannot add/update this record due to invalid references."
    elif error_code == 1217:  # Cannot delete or update a parent row (foreign key constraint)
        return "Cannot delete this record as it would break existing relationships."
    else:
        return f"Database error during {operation}: {str(e)}"

def get_table_schema(table_name):
    """Get the schema of a table"""
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute(f"DESCRIBE {table_name}")
            return cursor.fetchall()
    except Exception as e:
        print(f"Error getting schema for {table_name}: {str(e)}")
        return None
    finally:
        if 'conn' in locals():
            conn.close()

# ─── Home ────────────────────────────────────────────────────────────────────────
@app.route('/')
def index():
    """Home page route"""
    return render_template('index.html')

# ─── AIRLINE ─────────────────────────────────────────────────────────────────────
@app.route('/airlines')
def airlines():
    """Display all airlines"""
    conn = None
    try:
        conn = get_db_connection()
        if not conn:
            flash("Database connection error", "danger")
            return render_template('airlines.html', airlines=[])
            
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM airline;")
            data = cur.fetchall()
        return render_template('airlines.html', airlines=data)
    except Exception as e:
        flash(handle_db_error(e, "fetching airlines"), "danger")
        return render_template('airlines.html', airlines=[])
    finally:
        if conn:
            conn.close()

@app.route('/airlines/add', methods=['POST'])
def add_airline():
    try:
        f = request.form
        sql = "INSERT INTO airline (airlineID, revenue) VALUES (%s,%s);"
        conn = get_db_connection()
        with conn, conn.cursor() as cur:
            cur.execute(sql, (f['airlineID'], f.get('revenue') or None))
            conn.commit()
        flash('Airline added successfully!', 'success')
    except Exception as e:
        flash(handle_db_error(e, "adding airline"), "danger")
    return redirect(url_for('airlines'))

@app.route('/airlines/edit/<aid>', methods=['GET','POST'])
def edit_airline(aid):
    conn = None
    try:
        conn = get_db_connection()
        if not conn:
            flash("Database connection error", "danger")
            return redirect(url_for('airlines'))
            
        if request.method == 'POST':
            try:
                f = request.form
                sql = "UPDATE airline SET revenue=%s WHERE airlineID=%s;"
                with conn.cursor() as cur:
                    cur.execute(sql, (f.get('revenue') or None, aid))
                    conn.commit()
                flash('Airline updated successfully!', 'success')
                return redirect(url_for('airlines'))
            except Exception as e:
                flash(handle_db_error(e, "updating airline"), "danger")
                return redirect(url_for('airlines'))
        
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM airline WHERE airlineID=%s;", (aid,))
            rec = cur.fetchone()
        if not rec:
            flash("Airline not found.", "danger")
            return redirect(url_for('airlines'))
        return render_template('edit_airline.html', airline=rec)
    except Exception as e:
        flash(handle_db_error(e, "fetching airline"), "danger")
        return redirect(url_for('airlines'))
    finally:
        if conn:
            conn.close()

@app.route('/airlines/delete/<aid>', methods=['POST'])
def delete_airline(aid):
    try:
        conn = get_db_connection()
        with conn, conn.cursor() as cur:
            cur.execute("DELETE FROM airline WHERE airlineID=%s;", (aid,))
            conn.commit()
        flash('Airline deleted successfully!', 'success')
    except Exception as e:
        flash(handle_db_error(e, "deleting airline"), "danger")
    return redirect(url_for('airlines'))

# ─── AIRPORT ─────────────────────────────────────────────────────────────────────
@app.route('/airports')
def airports():
    """Display all airports"""
    conn = None
    try:
        conn = get_db_connection()
        if not conn:
            flash("Database connection error", "danger")
            return render_template('airports.html', airports=[])
            
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM airport;")
            data = cur.fetchall()
        return render_template('airports.html', airports=data)
    except Exception as e:
        flash(handle_db_error(e, "fetching airports"), "danger")
        return render_template('airports.html', airports=[])
    finally:
        if conn:
            conn.close()

@app.route('/airports/add', methods=['POST'])
def add_airport():
    conn = None
    try:
        conn = get_db_connection()
        if not conn:
            flash("Database connection error", "danger")
            return redirect(url_for('airports'))
            
        f = request.form
        sql = """
        INSERT INTO airport (airportID, airport_name, city, state, country, locationID)
        VALUES (%s, %s, %s, %s, %s, %s);
        """
        with conn.cursor() as cur:
            cur.execute(sql, (
                f['airportID'],
                f.get('airport_name'),
                f['city'],
                f['state'],
                f['country'],
                f['locationID']
            ))
            conn.commit()
        flash('Airport added successfully!', 'success')
    except Exception as e:
        flash(handle_db_error(e, "adding airport"), "danger")
    finally:
        if conn:
            conn.close()
    return redirect(url_for('airports'))

@app.route('/airports/edit/<string:airportID>', methods=['GET', 'POST'])
def edit_airport(airportID):
    conn = None
    try:
        conn = get_db_connection()
        if not conn:
            flash("Database connection error", "danger")
            return redirect(url_for('airports'))
            
        if request.method == 'POST':
            try:
                f = request.form
                sql = """
                UPDATE airport 
                SET airport_name=%s, city=%s, state=%s, country=%s, locationID=%s
                WHERE airportID=%s;
                """
                with conn.cursor() as cur:
                    cur.execute(sql, (
                        f.get('airport_name'),
                        f['city'],
                        f['state'],
                        f['country'],
                        f['locationID'],
                        airportID
                    ))
                    conn.commit()
                flash('Airport updated successfully!', 'success')
                return redirect(url_for('airports'))
            except Exception as e:
                flash(handle_db_error(e, "updating airport"), "danger")
                return redirect(url_for('airports'))
        
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM airport WHERE airportID=%s;", (airportID,))
            rec = cur.fetchone()
        if not rec:
            flash("Airport not found.", "danger")
            return redirect(url_for('airports'))
        return render_template('edit_airport.html', airport=rec)
    except Exception as e:
        flash(handle_db_error(e, "fetching airport"), "danger")
        return redirect(url_for('airports'))
    finally:
        if conn:
            conn.close()

@app.route('/airports/delete/<string:airportID>', methods=['POST'])
def delete_airport(airportID):
    conn = None
    try:
        conn = get_db_connection()
        if not conn:
            flash("Database connection error", "danger")
            return redirect(url_for('airports'))
            
        with conn.cursor() as cur:
            cur.execute("DELETE FROM airport WHERE airportID=%s;", (airportID,))
            conn.commit()
        flash('Airport deleted successfully!', 'success')
    except Exception as e:
        flash(handle_db_error(e, "deleting airport"), "danger")
    finally:
        if conn:
            conn.close()
    return redirect(url_for('airports'))

# ─── FLIGHTS ─────────────────────────────────────────────────────────────────────
@app.route('/flights')
def flights():
    """Display all flights"""
    conn = None
    try:
        conn = get_db_connection()
        if not conn:
            flash("Database connection error", "danger")
            return render_template('flights.html', flights=[])
            
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM flight;")
            data = cur.fetchall()
        return render_template('flights.html', flights=data)
    except Exception as e:
        flash(handle_db_error(e, "fetching flights"), "danger")
        return render_template('flights.html', flights=[])
    finally:
        if conn:
            conn.close()

@app.route('/flights/add', methods=['POST'])
def add_flight():
    try:
        f = request.form
        sql = """
        INSERT INTO flight (flightID, routeID, support_airline, support_tail, progress, airplane_status, next_time)
        VALUES (%s, %s, %s, %s, %s, %s, %s);
        """
        conn = get_db_connection()
        with conn, conn.cursor() as cur:
            cur.execute(sql, (
                f['flightID'],
                f.get('routeID'),
                f.get('support_airline'),
                f.get('support_tail'),
                f.get('progress'),
                f.get('airplane_status'),
                f.get('next_time')
            ))
            conn.commit()
        flash('Flight added successfully!', 'success')
    except Exception as e:
        flash(handle_db_error(e, "adding flight"), "danger")
    return redirect(url_for('flights'))

@app.route('/flights/edit/<fid>', methods=['GET','POST'])
def edit_flight(fid):
    conn = None
    try:
        conn = get_db_connection()
        if not conn:
            flash("Database connection error", "danger")
            return redirect(url_for('flights'))
            
        if request.method == 'POST':
            try:
                f = request.form
                sql = """
                UPDATE flight 
                SET routeID=%s, support_airline=%s, support_tail=%s, progress=%s, airplane_status=%s, next_time=%s
                WHERE flightID=%s;
                """
                with conn.cursor() as cur:
                    cur.execute(sql, (
                        f.get('routeID'),
                        f.get('support_airline'),
                        f.get('support_tail'),
                        f.get('progress'),
                        f.get('airplane_status'),
                        f.get('next_time'),
                        fid
                    ))
                    conn.commit()
                flash('Flight updated successfully!', 'success')
                return redirect(url_for('flights'))
            except Exception as e:
                flash(handle_db_error(e, "updating flight"), "danger")
                return redirect(url_for('flights'))
        
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM flight WHERE flightID=%s;", (fid,))
            rec = cur.fetchone()
        if not rec:
            flash("Flight not found.", "danger")
            return redirect(url_for('flights'))
        return render_template('edit_flight.html', flight=rec)
    except Exception as e:
        flash(handle_db_error(e, "fetching flight"), "danger")
        return redirect(url_for('flights'))
    finally:
        if conn:
            conn.close()

@app.route('/flights/delete/<fid>', methods=['POST'])
def delete_flight(fid):
    try:
        conn = get_db_connection()
        with conn, conn.cursor() as cur:
            cur.execute("DELETE FROM flight WHERE flightID=%s;", (fid,))
            conn.commit()
        flash('Flight deleted successfully!', 'success')
    except Exception as e:
        flash(handle_db_error(e, "deleting flight"), "danger")
    return redirect(url_for('flights'))

# ─── PASSENGERS ──────────────────────────────────────────────────────────────────
@app.route('/passengers')
def passengers():
    """Display all passengers"""
    conn = None
    try:
        conn = get_db_connection()
        if not conn:
            flash("Database connection error", "danger")
            return render_template('passengers.html', passengers=[])
            
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM passenger;")
            data = cur.fetchall()
        return render_template('passengers.html', passengers=data)
    except Exception as e:
        flash(handle_db_error(e, "fetching passengers"), "danger")
        return render_template('passengers.html', passengers=[])
    finally:
        if conn:
            conn.close()

# ─── PILOTS ──────────────────────────────────────────────────────────────────────
@app.route('/pilots')
def pilots():
    """Display all pilots"""
    conn = None
    try:
        conn = get_db_connection()
        if not conn:
            flash("Database connection error", "danger")
            return render_template('pilots.html', pilots=[])
            
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM pilot;")
            data = cur.fetchall()
        return render_template('pilots.html', pilots=data)
    except Exception as e:
        flash(handle_db_error(e, "fetching pilots"), "danger")
        return render_template('pilots.html', pilots=[])
    finally:
        if conn:
            conn.close()

@app.route('/pilots/add', methods=['POST'])
def add_pilot():
    try:
        f = request.form
        sql = """
        INSERT INTO pilot (personID, taxID, experience, commanding_flight)
        VALUES (%s, %s, %s, %s);
        """
        conn = get_db_connection()
        with conn, conn.cursor() as cur:
            cur.execute(sql, (
                f['personID'],
                f['taxID'],
                f.get('experience'),
                f.get('commanding_flight')
            ))
            conn.commit()
        flash('Pilot added successfully!', 'success')
    except Exception as e:
        flash(handle_db_error(e, "adding pilot"), "danger")
    return redirect(url_for('pilots'))

@app.route('/pilots/edit/<pid>', methods=['GET','POST'])
def edit_pilot(pid):
    conn = None
    try:
        conn = get_db_connection()
        if request.method=='POST':
            try:
                f = request.form
                sql = """
                UPDATE pilot 
                SET taxID=%s, experience=%s, commanding_flight=%s
                WHERE personID=%s;
                """
                with conn.cursor() as cur:
                    cur.execute(sql, (
                        f['taxID'],
                        f.get('experience'),
                        f.get('commanding_flight'),
                        pid
                    ))
                    conn.commit()
                flash('Pilot updated successfully!', 'success')
                return redirect(url_for('pilots'))
            except Exception as e:
                flash(handle_db_error(e, "updating pilot"), "danger")
        
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM pilot WHERE personID=%s;", (pid,))
            rec = cur.fetchone()
        if not rec:
            flash("Pilot not found.", "danger")
            return redirect(url_for('pilots'))
        return render_template('edit_pilot.html', pilot=rec)
    except Exception as e:
        flash(handle_db_error(e, "fetching pilot"), "danger")
        return redirect(url_for('pilots'))
    finally:
        if conn:
            conn.close()

@app.route('/pilots/delete/<pid>', methods=['POST'])
def delete_pilot(pid):
    try:
        conn = get_db_connection()
        with conn, conn.cursor() as cur:
            cur.execute("DELETE FROM pilot WHERE personID=%s;", (pid,))
            conn.commit()
        flash('Pilot deleted successfully!', 'success')
    except Exception as e:
        flash(handle_db_error(e, "deleting pilot"), "danger")
    return redirect(url_for('pilots'))

# ─── RESERVATIONS ────────────────────────────────────────────────────────────────
@app.route('/reservations')
def reservations():
    """Display all reservations"""
    conn = None
    try:
        conn = get_db_connection()
        if not conn:
            flash("Database connection error", "danger")
            return render_template('reservations.html', reservations=[])
            
        with conn.cursor() as cur:
            # Create reservation table if it doesn't exist
            cur.execute("""
                CREATE TABLE IF NOT EXISTS reservation (
                    personID VARCHAR(50) NOT NULL,
                    airportID CHAR(3) NOT NULL,
                    sequence INT NOT NULL,
                    PRIMARY KEY (personID, airportID),
                    FOREIGN KEY (personID) REFERENCES person(personID),
                    FOREIGN KEY (airportID) REFERENCES airport(airportID)
                )
            """)
            conn.commit()
            
            cur.execute("SELECT * FROM reservation;")
            data = cur.fetchall()
        return render_template('reservations.html', reservations=data)
    except Exception as e:
        flash(handle_db_error(e, "fetching reservations"), "danger")
        return render_template('reservations.html', reservations=[])
    finally:
        if conn:
            conn.close()

@app.route('/reservations/add', methods=['POST'])
def add_reservation():
    conn = None
    try:
        conn = get_db_connection()
        if not conn:
            flash("Database connection error", "danger")
            return redirect(url_for('reservations'))
            
        f = request.form
        sql = """
        INSERT INTO reservation (personID, airportID, sequence)
        VALUES (%s, %s, %s);
        """
        with conn.cursor() as cur:
            cur.execute(sql, (
                f['personID'],
                f['airportID'],
                f['sequence']
            ))
            conn.commit()
        flash('Reservation added successfully!', 'success')
    except Exception as e:
        flash(handle_db_error(e, "adding reservation"), "danger")
    finally:
        if conn:
            conn.close()
    return redirect(url_for('reservations'))

@app.route('/reservations/delete/<pid>/<aid>', methods=['POST'])
def delete_reservation(pid, aid):
    conn = None
    try:
        conn = get_db_connection()
        if not conn:
            flash("Database connection error", "danger")
            return redirect(url_for('reservations'))
            
        with conn.cursor() as cur:
            cur.execute("DELETE FROM reservation WHERE personID=%s AND airportID=%s;", (pid, aid))
            conn.commit()
        flash('Reservation deleted successfully!', 'success')
    except Exception as e:
        flash(handle_db_error(e, "deleting reservation"), "danger")
    finally:
        if conn:
            conn.close()
    return redirect(url_for('reservations'))

@app.route('/health')
def health_check():
    """Health check endpoint"""
    conn = None
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({'status': 'error', 'message': 'Database connection failed'}), 500
        return jsonify({'status': 'healthy'})
    finally:
        if conn:
            conn.close()

if __name__ == '__main__':
    app.run(debug=True) 