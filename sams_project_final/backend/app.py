# backend/app.py

from flask import Flask, render_template, request, redirect, url_for
import pymysql
from pymysql.cursors import DictCursor

app = Flask(__name__, template_folder='../frontend/templates')

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


# ─── Home ────────────────────────────────────────────────────────────────────────
@app.route('/')
def index():
    return render_template('index.html')


# ─── AIRLINE ─────────────────────────────────────────────────────────────────────
@app.route('/airlines')
def airlines():
    conn = get_db_connection()
    with conn, conn.cursor() as cur:
        cur.execute("SELECT * FROM airline;")
        data = cur.fetchall()
    return render_template('airlines.html', airlines=data)

@app.route('/airlines/add', methods=['POST'])
def add_airline():
    f = request.form
    sql = "INSERT INTO airline (airlineID, revenue) VALUES (%s,%s);"
    conn = get_db_connection()
    with conn, conn.cursor() as cur:
        cur.execute(sql, (f['airlineID'], f.get('revenue') or None))
        conn.commit()
    return redirect(url_for('airlines'))

@app.route('/airlines/edit/<aid>', methods=['GET','POST'])
def edit_airline(aid):
    conn = get_db_connection()
    if request.method=='POST':
        f = request.form
        sql = "UPDATE airline SET revenue=%s WHERE airlineID=%s;"
        with conn, conn.cursor() as cur:
            cur.execute(sql, (f.get('revenue') or None, aid))
            conn.commit()
        return redirect(url_for('airlines'))
    with conn, conn.cursor() as cur:
        cur.execute("SELECT * FROM airline WHERE airlineID=%s;", (aid,))
        rec = cur.fetchone()
    return render_template('edit_airline.html', airline=rec)

@app.route('/airlines/delete/<aid>', methods=['POST'])
def delete_airline(aid):
    conn = get_db_connection()
    with conn, conn.cursor() as cur:
        cur.execute("DELETE FROM airline WHERE airlineID=%s;", (aid,))
        conn.commit()
    return redirect(url_for('airlines'))


# ─── AIRPORT ────────────────────────────────────────────────────────────────────
@app.route('/airports')
def airports():
    conn = get_db_connection()
    with conn, conn.cursor() as cur:
        cur.execute("SELECT * FROM airport;")
        data = cur.fetchall()
    return render_template('airports.html', airports=data)

@app.route('/airports/add', methods=['POST'])
def add_airport():
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
    return redirect(url_for('airports'))

@app.route('/airports/edit/<aid>', methods=['GET','POST'])
def edit_airport(aid):
    conn = get_db_connection()
    if request.method=='POST':
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
        return redirect(url_for('airports'))
    with conn, conn.cursor() as cur:
        cur.execute("SELECT * FROM airport WHERE airportID=%s;", (aid,))
        rec = cur.fetchone()
    return render_template('edit_airport.html', airport=rec)

@app.route('/airports/delete/<aid>', methods=['POST'])
def delete_airport(aid):
    conn = get_db_connection()
    with conn, conn.cursor() as cur:
        cur.execute("DELETE FROM airport WHERE airportID=%s;", (aid,))
        conn.commit()
    return redirect(url_for('airports'))


# ─── FLIGHT ─────────────────────────────────────────────────────────────────────
@app.route('/flights')
def flights():
    conn = get_db_connection()
    with conn, conn.cursor() as cur:
        cur.execute("SELECT * FROM flight;")
        data = cur.fetchall()
    return render_template('flights.html', flights=data)

@app.route('/flights/add', methods=['POST'])
def add_flight():
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
    return redirect(url_for('flights'))

@app.route('/flights/edit/<fid>', methods=['GET','POST'])
def edit_flight(fid):
    conn = get_db_connection()
    if request.method=='POST':
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
        return redirect(url_for('flights'))
    with conn, conn.cursor() as cur:
        cur.execute("SELECT * FROM flight WHERE flightID=%s;", (fid,))
        rec = cur.fetchone()
    return render_template('edit_flight.html', flight=rec)

@app.route('/flights/delete/<fid>', methods=['POST'])
def delete_flight(fid):
    conn = get_db_connection()
    with conn, conn.cursor() as cur:
        cur.execute("DELETE FROM flight WHERE flightID=%s;", (fid,))
        conn.commit()
    return redirect(url_for('flights'))


# ─── PASSENGERS ──────────────────────────────────────────────────────────────────
@app.route('/passengers')
def passengers():
    conn = get_db_connection()
    with conn, conn.cursor() as cur:
        cur.execute("SELECT * FROM passenger;")
        data = cur.fetchall()
    return render_template('passengers.html', passengers=data)


# ─── PILOTS ──────────────────────────────────────────────────────────────────────
@app.route('/pilots')
def pilots():
    conn = get_db_connection()
    with conn, conn.cursor() as cur:
        cur.execute("SELECT * FROM pilot;")
        data = cur.fetchall()
    return render_template('pilots.html', pilots=data)


# ─── RESERVATIONS ───────────────────────────────────────────────────────────────
@app.route('/reservations')
def reservations():
    conn = get_db_connection()
    with conn, conn.cursor() as cur:
        cur.execute("SELECT * FROM passenger_vacations;")
        data = cur.fetchall()
    return render_template('reservations.html', reservations=data)


if __name__ == "__main__":
    app.run(debug=True, port=5002)
