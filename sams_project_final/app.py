@app.route('/airports/add', methods=['POST'])
def add_airport():
    conn = None
    try:
        conn = get_db_connection()
        if not conn:
            flash("Database connection error", "danger")
            return redirect(url_for('airports'))
            
        f = request.form
        
        with conn.cursor() as cur:
            cur.callproc('add_airport', (
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

@app.route('/retire_flight', methods=['GET', 'POST'])
def retire_flight():
    if request.method == 'POST':
        conn = None
        try:
            conn = get_db_connection()
            if not conn:
                flash("Database connection error", "danger")
                return redirect(url_for('retire_flight'))
            
            flight_id = request.form.get('flight_id')
            
            with conn.cursor() as cur:
                # First get the airplane's locationID
                cur.execute("""
                    SELECT a.locationID 
                    FROM airplane a 
                    JOIN flight f ON a.airlineID = f.support_airline AND a.tail_num = f.support_tail 
                    WHERE f.flightID = %s
                """, (flight_id,))
                result = cur.fetchone()
                
                if result:
                    location_id = result['locationID']
                    # Call the stored procedure to retire the flight
                    cur.callproc('retire_flight', (flight_id,))
                    # Delete the location if it exists
                    if location_id:
                        cur.execute("DELETE FROM location WHERE locationID = %s", (location_id,))
                    conn.commit()
                    flash('Flight retired successfully!', 'success')
                else:
                    flash('Flight not found or no associated airplane', 'warning')
        except Exception as e:
            flash(handle_db_error(e, "retiring flight"), "danger")
        finally:
            if conn:
                conn.close()
        return redirect(url_for('retire_flight'))
    return render_template('retire_flight.html')

@app.route('/passengers_disembark', methods=['GET', 'POST'])
def passengers_disembark():
    if request.method == 'POST':
        conn = None
        try:
            conn = get_db_connection()
            if not conn:
                flash("Database connection error", "danger")
                return redirect(url_for('passengers_disembark'))
            
            flight_id = request.form.get('flight_id')
            
            with conn.cursor() as cur:
                # First get all passenger locationIDs for this flight
                cur.execute("""
                    SELECT p.locationID 
                    FROM person p 
                    JOIN passenger pa ON p.personID = pa.personID 
                    JOIN reservation r ON pa.personID = r.passengerID 
                    WHERE r.flightID = %s AND p.locationID IS NOT NULL
                """, (flight_id,))
                location_ids = [row['locationID'] for row in cur.fetchall()]
                
                # Call the stored procedure to disembark passengers
                cur.callproc('passengers_disembark', (flight_id,))
                
                # Delete the locations
                for location_id in location_ids:
                    cur.execute("DELETE FROM location WHERE locationID = %s", (location_id,))
                
                conn.commit()
                flash('Passengers disembarked successfully!', 'success')
        except Exception as e:
            flash(handle_db_error(e, "disembarking passengers"), "danger")
        finally:
            if conn:
                conn.close()
        return redirect(url_for('passengers_disembark'))
    return render_template('passengers_disembark.html')

@app.route('/flight_landing', methods=['GET', 'POST'])
def flight_landing():
    if request.method == 'POST':
        conn = None
        try:
            conn = get_db_connection()
            if not conn:
                flash("Database connection error", "danger")
                return redirect(url_for('flight_landing'))
            
            flight_id = request.form.get('flight_id')
            
            with conn.cursor() as cur:
                # First get the airplane's locationID
                cur.execute("""
                    SELECT a.locationID 
                    FROM airplane a 
                    JOIN flight f ON a.airlineID = f.support_airline AND a.tail_num = f.support_tail 
                    WHERE f.flightID = %s
                """, (flight_id,))
                result = cur.fetchone()
                
                if result:
                    location_id = result['locationID']
                    # Call the stored procedure to land the flight
                    cur.callproc('flight_landing', (flight_id,))
                    # Update the location if it exists
                    if location_id:
                        cur.execute("""
                            UPDATE location 
                            SET locationID = %s 
                            WHERE locationID = %s
                        """, (f'airport_{flight_id}', location_id))
                    conn.commit()
                    flash('Flight landed successfully!', 'success')
                else:
                    flash('Flight not found or no associated airplane', 'warning')
        except Exception as e:
            flash(handle_db_error(e, "landing flight"), "danger")
        finally:
            if conn:
                conn.close()
        return redirect(url_for('flight_landing'))
    return render_template('flight_landing.html')

@app.route('/flights_in_the_air')
def flights_in_the_air():
    conn = None
    try:
        conn = get_db_connection()
        if not conn:
            flash("Database connection error", "danger")
            return redirect(url_for('index'))
        
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM flights_in_the_air")
            flights = cur.fetchall()
            
        return render_template('flights_in_the_air.html', flights=flights)
    except Exception as e:
        flash(handle_db_error(e, "viewing flights in the air"), "danger")
        return redirect(url_for('index'))
    finally:
        if conn:
            conn.close()
    return render_template('flight_landing.html')

@app.route('/add_person', methods=['GET', 'POST'])
def add_person():
    if request.method == 'POST':
        conn = None
        try:
            conn = get_db_connection()
            if not conn:
                flash("Database connection error", "danger")
                return redirect(url_for('add_person'))
            
            f = request.form
            person_type = f.get('person_type')
            
            with conn.cursor() as cur:
                if person_type == 'pilot':
                    # Add a pilot
                    cur.callproc('add_person', (
                        f['personID'],
                        f['first_name'],
                        f.get('last_name'),
                        f['locationID'],
                        f['taxID'],
                        int(f['experience']),
                        None,
                        None
                    ))
                elif person_type == 'passenger':
                    # Add a passenger
                    cur.callproc('add_person', (
                        f['personID'],
                        f['first_name'],
                        f.get('last_name'),
                        f['locationID'],
                        None,
                        None,
                        int(f['miles']),
                        int(f['funds'])
                    ))
                else:
                    flash('Invalid person type', 'danger')
                    return redirect(url_for('add_person'))
                
                conn.commit()
                flash('Person added successfully!', 'success')
        except Exception as e:
            flash(handle_db_error(e, "adding person"), "danger")
        finally:
            if conn:
                conn.close()
        return redirect(url_for('add_person'))
    return render_template('add_person.html') 