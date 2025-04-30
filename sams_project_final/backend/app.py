# backend/app.py

from flask import Flask, render_template, request, redirect, url_for, flash
import pymysql
from pymysql.cursors import DictCursor
import os

app = Flask(__name__, 
           template_folder='../frontend/templates',
           static_folder='../frontend/static')

# Set a secret key for flash messages
app.secret_key = 'your-secret-key-here'  # Change this to a secure secret key

DB_CONFIG = {
    'host':     '127.0.0.1',
    'user':     'root', #newuser
    'password': 'SheSeekMyWellFR9', #flight123456
    'db':       'flight_tracking',  # Changed from SQL file name to actual database name
    'cursorclass': DictCursor,
    'port':     3306
}



def get_db_connection():
    return pymysql.connect(**DB_CONFIG)

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

# ─── Home ────────────────────────────────────────────────────────────────────────
@app.route('/')
def index():
    return render_template('index.html')


# ─── AIRLINE ─────────────────────────────────────────────────────────────────────
@app.route('/airlines')
def airlines():
    try:
        conn = get_db_connection()
        with conn, conn.cursor() as cur:
            cur.execute("SELECT * FROM airline;")
            data = cur.fetchall()
        return render_template('airlines.html', airlines=data)
    except Exception as e:
        flash(handle_db_error(e, "fetching airlines"), "danger")
        return render_template('airlines.html', airlines=[])

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
    conn = get_db_connection()
    if request.method=='POST':
        try:
            f = request.form
            sql = "UPDATE airline SET revenue=%s WHERE airlineID=%s;"
            with conn, conn.cursor() as cur:
                cur.execute(sql, (f.get('revenue') or None, aid))
                conn.commit()
            flash('Airline updated successfully!', 'success')
            return redirect(url_for('airlines'))
        except Exception as e:
            flash(handle_db_error(e, "updating airline"), "danger")
    try:
        with conn, conn.cursor() as cur:
            cur.execute("SELECT * FROM airline WHERE airlineID=%s;", (aid,))
            rec = cur.fetchone()
        if not rec:
            flash("Airline not found.", "danger")
            return redirect(url_for('airlines'))
        return render_template('edit_airline.html', airline=rec)
    except Exception as e:
        flash(handle_db_error(e, "fetching airline"), "danger")
        return redirect(url_for('airlines'))

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


# ─── AIRPORT ────────────────────────────────────────────────────────────────────
@app.route('/airports')
def airports():
    try:
        conn = get_db_connection()
        with conn, conn.cursor() as cur:
            cur.execute("SELECT * FROM airport;")
            data = cur.fetchall()
        return render_template('airports.html', airports=data)
    except Exception as e:
        flash(handle_db_error(e, "fetching airports"), "danger")
        return render_template('airports.html', airports=[])

@app.route('/airports/add', methods=['POST'])
def add_airport():
    try:
        f = request.form
        sql = """INSERT INTO airport
              (airportID, airport_name, city, state, country, locationID)
              VALUES (%s,%s,%s,%s,%s,%s);"""
        conn = get_db_connection()
        with conn, conn.cursor() as cur:
            cur.execute(sql, (
              f['airportID'], f.get('airport_name') or None,
              f['city'], f['state'], f['country'], f.get('locationID') or None
            ))
            conn.commit()
        flash('Airport added successfully!', 'success')
    except Exception as e:
        flash(handle_db_error(e, "adding airport"), "danger")
    return redirect(url_for('airports'))

@app.route('/airports/edit/<aid>', methods=['GET','POST'])
def edit_airport(aid):
    conn = get_db_connection()
    if request.method=='POST':
        try:
            f = request.form
            sql = """UPDATE airport
                     SET airport_name=%s, city=%s, state=%s, country=%s, locationID=%s
                     WHERE airportID=%s;"""
            with conn, conn.cursor() as cur:
                cur.execute(sql, (
                    f.get('airport_name') or None,
                    f['city'], f['state'], f['country'], f.get('locationID') or None,
                    aid
                ))
                conn.commit()
            flash('Airport updated successfully!', 'success')
            return redirect(url_for('airports'))
        except Exception as e:
            flash(handle_db_error(e, "updating airport"), "danger")
    try:
        with conn, conn.cursor() as cur:
            cur.execute("SELECT * FROM airport WHERE airportID=%s;", (aid,))
            rec = cur.fetchone()
        if not rec:
            flash("Airport not found.", "danger")
            return redirect(url_for('airports'))
        return render_template('edit_airport.html', airport=rec)
    except Exception as e:
        flash(handle_db_error(e, "fetching airport"), "danger")
        return redirect(url_for('airports'))

@app.route('/airports/delete/<aid>', methods=['POST'])
def delete_airport(aid):
    try:
        conn = get_db_connection()
        with conn, conn.cursor() as cur:
            cur.execute("DELETE FROM airport WHERE airportID=%s;", (aid,))
            conn.commit()
        flash('Airport deleted successfully!', 'success')
    except Exception as e:
        flash(handle_db_error(e, "deleting airport"), "danger")
    return redirect(url_for('airports'))


# ─── FLIGHT ─────────────────────────────────────────────────────────────────────
@app.route('/flights')
def flights():
    try:
        conn = get_db_connection()
        with conn, conn.cursor() as cur:
            # Get flights in the air
            cur.execute("SELECT * FROM people_in_the_air;")
            flights_air = cur.fetchall()
            
            # Get flights on the ground
            cur.execute("SELECT * FROM people_on_the_ground;")
            flights_ground = cur.fetchall()
            
        return render_template('flights.html', flights_air=flights_air, flights_ground=flights_ground)
    except Exception as e:
        flash(handle_db_error(e, "fetching flights"), "danger")
        return render_template('flights.html', flights_air=[], flights_ground=[])

@app.route('/flights/add', methods=['POST'])
def add_flight():
    try:
        f = request.form
        sql = """INSERT INTO flight
              (flightID, routeID, support_airline, support_tail,
               progress, airplane_status, next_time, cost)
              VALUES (%s,%s,%s,%s,%s,%s,%s,%s);"""
        conn = get_db_connection()
        with conn, conn.cursor() as cur:
            cur.execute(sql, (
              f['flightID'], f['routeID'], f.get('support_airline') or None,
              f.get('support_tail') or None, f.get('progress') or None,
              f.get('airplane_status') or None, f.get('next_time') or None,
              f.get('cost') or 0
            ))
            conn.commit()
        flash('Flight added successfully!', 'success')
    except Exception as e:
        flash(handle_db_error(e, "adding flight"), "danger")
    return redirect(url_for('flights'))

@app.route('/flights/edit/<fid>', methods=['GET','POST'])
def edit_flight(fid):
    conn = get_db_connection()
    if request.method=='POST':
        try:
            f = request.form
            sql = """UPDATE flight
                     SET routeID=%s, support_airline=%s, support_tail=%s,
                         progress=%s, airplane_status=%s, next_time=%s, cost=%s
                     WHERE flightID=%s;"""
            with conn, conn.cursor() as cur:
                cur.execute(sql, (
                 f['routeID'], f.get('support_airline') or None,
                 f.get('support_tail') or None, f.get('progress') or None,
                 f.get('airplane_status') or None, f.get('next_time') or None,
                 f.get('cost') or 0, fid
                ))
                conn.commit()
            flash('Flight updated successfully!', 'success')
            return redirect(url_for('flights'))
        except Exception as e:
            flash(handle_db_error(e, "updating flight"), "danger")
    try:
        with conn, conn.cursor() as cur:
            cur.execute("SELECT * FROM flight WHERE flightID=%s;", (fid,))
            rec = cur.fetchone()
        if not rec:
            flash("Flight not found.", "danger")
            return redirect(url_for('flights'))
        return render_template('edit_flight.html', flight=rec)
    except Exception as e:
        flash(handle_db_error(e, "fetching flight"), "danger")
        return redirect(url_for('flights'))

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
    try:
        conn = get_db_connection()
        with conn, conn.cursor() as cur:
            cur.execute("SELECT * FROM passenger;")
            data = cur.fetchall()
        return render_template('passengers.html', passengers=data)
    except Exception as e:
        flash(handle_db_error(e, "fetching passengers"), "danger")
        return render_template('passengers.html', passengers=[])


# ─── PILOTS ──────────────────────────────────────────────────────────────────────
@app.route('/pilots')
def pilots():
    conn = get_db_connection()
    with conn, conn.cursor() as cur:
        cur.execute("SELECT * FROM pilot;")
        data = cur.fetchall()
    return render_template('pilots.html', pilots=data)

@app.route('/pilots/add', methods=['POST'])
def add_pilot():
    f = request.form
    sql = """INSERT INTO pilot
          (personID, taxID, experience, commanding_flight)
          VALUES (%s,%s,%s,%s);"""
    conn = get_db_connection()
    with conn, conn.cursor() as cur:
        cur.execute(sql, (
          f['personID'], f['taxID'],
          f['experience'], f.get('commanding_flight') or None
        ))
        conn.commit()
    return redirect(url_for('pilots'))

@app.route('/pilots/edit/<pid>', methods=['GET','POST'])
def edit_pilot(pid):
    conn = get_db_connection()
    if request.method=='POST':
        f = request.form
        sql = """UPDATE pilot
                 SET taxID=%s, experience=%s, commanding_flight=%s
                 WHERE personID=%s;"""
        with conn, conn.cursor() as cur:
            cur.execute(sql, (
                f['taxID'], f['experience'],
                f.get('commanding_flight') or None, pid
            ))
            conn.commit()
        return redirect(url_for('pilots'))
    with conn, conn.cursor() as cur:
        cur.execute("SELECT * FROM pilot WHERE personID=%s;", (pid,))
        rec = cur.fetchone()
    return render_template('edit_pilot.html', pilot=rec)

@app.route('/pilots/delete/<pid>', methods=['POST'])
def delete_pilot(pid):
    conn = get_db_connection()
    with conn, conn.cursor() as cur:
        cur.execute("DELETE FROM pilot WHERE personID=%s;", (pid,))
        conn.commit()
    return redirect(url_for('pilots'))


# ─── RESERVATIONS ───────────────────────────────────────────────────────────────
@app.route('/reservations')
def reservations():
    conn = get_db_connection()
    with conn, conn.cursor() as cur:
        cur.execute("SELECT * FROM passenger_vacations;")
        data = cur.fetchall()
    return render_template('reservations.html', reservations=data)

@app.route('/reservations/add', methods=['POST'])
def add_reservation():
    f = request.form
    sql = """INSERT INTO passenger_vacations
          (personID, airportID, sequence)
          VALUES (%s,%s,%s);"""
    conn = get_db_connection()
    with conn, conn.cursor() as cur:
        cur.execute(sql, (
          f['personID'], f['airportID'], f['sequence']
        ))
        conn.commit()
    return redirect(url_for('reservations'))

@app.route('/reservations/delete/<pid>/<aid>', methods=['POST'])
def delete_reservation(pid, aid):
    conn = get_db_connection()
    with conn, conn.cursor() as cur:
        cur.execute("DELETE FROM passenger_vacations WHERE personID=%s AND airportID=%s;", (pid, aid))
        conn.commit()
    return redirect(url_for('reservations'))


if __name__ == "__main__":
    app.run(debug=True, port=5002)
