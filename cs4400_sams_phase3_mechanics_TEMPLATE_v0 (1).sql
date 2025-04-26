-- CS4400: Introduction to Database Systems: Monday, March 3, 2025
-- Simple Airline Management System Course Project Mechanics [TEMPLATE] (v0)
-- Views, Functions & Stored Procedures

/* This is a standard preamble for most of our scripts.  The intent is to establish
a consistent environment for the database behavior. */
set global transaction isolation level serializable;
set global SQL_MODE = 'ANSI,TRADITIONAL';
set names utf8mb4;
set SQL_SAFE_UPDATES = 0;

set @thisDatabase = 'flight_tracking';
use flight_tracking;
-- -----------------------------------------------------------------------------
-- stored procedures and views
-- -----------------------------------------------------------------------------
/* Standard Procedure: If one or more of the necessary conditions for a procedure to
be executed is false, then simply have the procedure halt execution without changing
the database state. Do NOT display any error messages, etc. */

-- [_] supporting functions, views and stored procedures
-- -----------------------------------------------------------------------------
/* Helpful library capabilities to simplify the implementation of the required
views and procedures. */
-- -----------------------------------------------------------------------------
drop function if exists leg_time;
delimiter //
create function leg_time (ip_distance integer, ip_speed integer)
	returns time reads sql data
begin
	declare total_time decimal(10,2);
    declare hours, minutes integer default 0;
    set total_time = ip_distance / ip_speed;
    set hours = truncate(total_time, 0);
    set minutes = truncate((total_time - hours) * 60, 0);
    return maketime(hours, minutes, 0);
end //
delimiter ;

-- [1] add_airplane()
-- -----------------------------------------------------------------------------
/* This stored procedure creates a new airplane.  A new airplane must be sponsored
by an existing airline, and must have a unique tail number for that airline.
username.  An airplane must also have a non-zero seat capacity and speed. An airplane
might also have other factors depending on it's type, like the model and the engine.  
Finally, an airplane must have a new and database-wide unique location
since it will be used to carry passengers. */
-- -----------------------------------------------------------------------------
drop procedure if exists add_airplane;
delimiter //
create procedure add_airplane (in ip_airlineID varchar(50), in ip_tail_num varchar(50),
	in ip_seat_capacity integer, in ip_speed integer, in ip_locationID varchar(50),
    in ip_plane_type varchar(100), in ip_maintenanced boolean, in ip_model varchar(50),
    in ip_neo boolean)
sp_main: begin
	if ip_airlineID is null then
		LEAVE sp_main;
	end if;
	if ip_tail_num is null then
		LEAVE sp_main;
	end if;
    if ip_airlineID not in (select airlineID from airline) then
        leave sp_main;
    end if;
    
	IF ip_seat_capacity IS NULL OR ip_speed IS NULL 
	   OR ip_seat_capacity <= 0 OR ip_speed <= 0 THEN
		LEAVE sp_main;
	END IF;
    
    if ip_plane_type not in ('Boeing', 'Airbus') and ip_plane_type is not null then
        leave sp_main;
    end if;
    
    if ip_plane_type = 'Boeing' then
        if ip_neo is not null or ip_maintenanced is null or ip_model is null then
            leave sp_main;
        end if;
    elseif ip_plane_type = 'Airbus' then
        if ip_maintenanced is not null or ip_model is not null or ip_neo is null then
            leave sp_main;
        end if;
    elseif ip_plane_type is null then
        if ip_maintenanced is not null or ip_model is not null or ip_neo is not null then
            leave sp_main;
        end if;
    end if;
    
    if exists (select 1 from airplane where airlineID = ip_airlineID and tail_num = ip_tail_num) then
        leave sp_main;
    end if;
    
    if ip_locationID in (select locationID from location) then
        leave sp_main;
    end if;
    
    -- Add location and airplane
    insert into location values (ip_locationID);
    insert into airplane values (ip_airlineID, ip_tail_num, ip_seat_capacity, ip_speed, 
                               ip_locationID, ip_plane_type, ip_maintenanced, ip_model, ip_neo);
end //
delimiter ;
-- call add_airplane('Delta', 'n281fc', 6, 500, 'plane_41', 'Airbus', null, null, TRUE);

-- -- [2] add_airport()
-- -- -----------------------------------------------------------------------------
-- /* This stored procedure creates a new airport.  A new airport must have a unique
-- identifier along with a new and database-wide unique location if it will be used
-- to support airplane takeoffs and landings.  An airport may have a longer, more
-- descriptive name.  An airport must also have a city, state, and country designation. */
-- -- -----------------------------------------------------------------------------
drop procedure if exists add_airport;
delimiter //
create procedure add_airport (in ip_airportID char(3), in ip_airport_name varchar(200),
    in ip_city varchar(100), in ip_state varchar(100), in ip_country char(3), in ip_locationID varchar(50))
sp_main: begin
    if ip_city is null then
		leave sp_main;
	end if;
	if ip_state is null then
		leave sp_main;
	end if;
	if ip_country is null then
		leave sp_main;
	end if;
	if ip_airportID is null then
		leave sp_main;
	end if;
    
    if ip_airportID in (select airportID from airport) then
        leave sp_main;
    end if;
    
    if ip_locationID in (select locationID from location) then
        leave sp_main;
    end if;
    
    insert into location values (ip_locationID);
    insert into airport values (ip_airportID, ip_airport_name, ip_city, ip_state, ip_country, ip_locationID);
end //
delimiter ;

-- [3] add_person()
-- -----------------------------------------------------------------------------
/* This stored procedure creates a new person.  A new person must reference a unique
identifier along with a database-wide unique location used to determine where the
person is currently located: either at an airport, or on an airplane, at any given
time.  A person must have a first name, and might also have a last name.

A person can hold a pilot role or a passenger role (exclusively).  As a pilot,
a person must have a tax identifier to receive pay, and an experience level.  As a
passenger, a person will have some amount of frequent flyer miles, along with a
certain amount of funds needed to purchase tickets for flights. */
-- -----------------------------------------------------------------------------
drop procedure if exists add_person;
delimiter //
create procedure add_person (in ip_personID varchar(50), in ip_first_name varchar(100),
    in ip_last_name varchar(100), in ip_locationID varchar(50), in ip_taxID varchar(50),
    in ip_experience integer, in ip_miles integer, in ip_funds integer)
sp_main: begin
	if ip_personID is null then
		leave sp_main;
	end if;
	if ip_first_name is null then
		leave sp_main;
	end if;
	if ip_locationID is null then
		leave sp_main;
	end if;
    
    if ip_personID in (select personID from person) then
        leave sp_main;
    end if;
    
    if ip_locationID not in (select locationID from location) then
        leave sp_main;
    end if;
    
    if ip_taxID is not null and ip_experience is not null then
        if ip_miles is not null or ip_funds is not null then
            leave sp_main;
        end if;
        if ip_taxID in (select taxID from pilot) then 
			leave sp_main;
		end if;
        if ip_experience < 0 then
			leave sp_main;
		end if;
        insert into person values (ip_personID, ip_first_name, ip_last_name, ip_locationID);
        insert into pilot values (ip_personID, ip_taxID, ip_experience, null);
    elseif ip_miles is not null and ip_funds is not null then
        if ip_taxID is not null or ip_experience is not null then
            leave sp_main;
        end if;
        if (ip_miles < 0 or ip_funds < 0) then
			leave sp_main;
		end if;
        insert into person values (ip_personID, ip_first_name, ip_last_name, ip_locationID);
        insert into passenger values (ip_personID, ip_miles, ip_funds);
    else
        leave sp_main;
    end if;
end //
delimiter ;

-- [4] grant_or_revoke_pilot_license()
-- -----------------------------------------------------------------------------
/* This stored procedure inverts the status of a pilot license.  If the license
doesn't exist, it must be created; and, if it aready exists, then it must be removed. */
-- -----------------------------------------------------------------------------
drop procedure if exists grant_or_revoke_pilot_license;
delimiter //
create procedure grant_or_revoke_pilot_license (in ip_personID varchar(50), in ip_license varchar(100))
sp_main: begin
	if ip_personID is null then
		leave sp_main;
	end if;
	if ip_license is null then
		leave sp_main;
	end if;
    if ip_personID not in (select personID from pilot) then
        leave sp_main;
    end if;
    
    if exists (select * from pilot_licenses 
        where personID = ip_personID and license = ip_license) then
        delete from pilot_licenses where personID = ip_personID and license = ip_license;
    else
        insert into pilot_licenses values (ip_personID, ip_license);
    end if;
end //
delimiter ;

-- [5] offer_flight
drop procedure if exists offer_flight;
delimiter //
create procedure offer_flight (in ip_flightID varchar(50), in ip_routeID varchar(50),
    in ip_support_airline varchar(50), in ip_support_tail varchar(50), in ip_progress integer,
    in ip_next_time time, in ip_cost integer)
sp_main: begin
	if ip_flightID is null then
		leave sp_main;
	end if;
	if ip_routeID is null then
		leave sp_main;
	end if;
    if ip_cost < 0 then 
		leave sp_main;
	end if;
    
    if ip_flightID in (select flightID from flight) then
        leave sp_main;
    end if;

    if ip_routeID not in (select routeID from route) then
        leave sp_main;
    end if;
    
    if ip_support_airline is not null and ip_support_tail is not null then
        if not exists (select * from airplane 
            where airlineID = ip_support_airline and tail_num = ip_support_tail) then
            leave sp_main;
        end if;
        
        if exists (select * from flight 
            where support_airline = ip_support_airline 
            and support_tail = ip_support_tail) then
            leave sp_main;
        end if;
    end if;
    
    if (ip_progress is null or ip_progress < 0 or ip_progress >= (
        select count(*) from route_path where routeID = ip_routeID
    )) then
        leave sp_main;
    end if;
    if (ip_next_time is null or ip_cost is null) then
		leave sp_main;
	end if;
    
    insert into flight values (ip_flightID, ip_routeID, ip_support_airline, 
        ip_support_tail, ip_progress, 'on_ground', ip_next_time, ip_cost);
end //
delimiter ;

-- [6] flight_landing
drop procedure if exists flight_landing;
delimiter //
create procedure flight_landing (in ip_flightID varchar(50))
sp_main: begin
    declare v_distance integer;
	if ip_flightID is null then
		leave sp_main;
	end if;
    if ip_flightID not in (
        select flightID from flight where airplane_status = 'in_flight'
    ) then
        leave sp_main;
    end if;
    
    select l.distance into v_distance
    from flight f
    join route_path rp on f.routeID = rp.routeID
    join leg l on rp.legID = l.legID
    where f.flightID = ip_flightID
      and rp.sequence = f.progress;
      
    update pilot
    set experience = experience + 1
    where commanding_flight = ip_flightID;
    
    update passenger pa
    join person pe on pa.personID = pe.personID
    join airplane a on pe.locationID = a.locationID
    join flight f on f.support_airline = a.airlineID 
                   and f.support_tail = a.tail_num
    set pa.miles = pa.miles + v_distance
    where f.flightID = ip_flightID;
    
    update flight
    set airplane_status = 'on_ground',
        next_time = addtime(next_time, '01:00:00')
    where flightID = ip_flightID;
end //
delimiter ;

-- [7] flight_takeoff
drop procedure if exists flight_takeoff;
delimiter //
create procedure flight_takeoff (in ip_flightID varchar(50))
sp_main: begin
    declare airplane_type varchar(50);
    declare pilot_count integer;
    declare leg_distance integer;
    declare airplane_speed integer;
    declare flight_time time;
    declare next_leg_sequence integer;
	if ip_flightID is null then
		leave sp_main;
	end if;
    if not exists (select 1 from flight where flightID = ip_flightID) then
        leave sp_main;
    end if;

    if not exists (select 1 from flight where flightID = ip_flightID and airplane_status = 'on_ground') then
        leave sp_main;
    end if;

    select progress + 1 into next_leg_sequence from flight where flightID = ip_flightID;
    if not exists (select 1 from route_path where routeID = (select routeID from flight where flightID = ip_flightID) and sequence = next_leg_sequence) then
        leave sp_main;
    end if;

    select a.plane_type, a.speed into airplane_type, airplane_speed
    from flight f
    join airplane a on f.support_airline = a.airlineID and f.support_tail = a.tail_num
    where f.flightID = ip_flightID;

    select count(*) into pilot_count from pilot where commanding_flight = ip_flightID;
    
    if (airplane_type = 'Boeing' and pilot_count < 2) or (airplane_type != 'Boeing' and pilot_count < 1) then
        update flight set next_time = addtime(next_time, '00:30:00') where flightID = ip_flightID;
        leave sp_main;
    end if;

    select l.distance into leg_distance
    from route_path rp
    join leg l on rp.legID = l.legID
    where rp.routeID = (select routeID from flight where flightID = ip_flightID) and rp.sequence = next_leg_sequence;

    set flight_time = sec_to_time(leg_distance / airplane_speed * 3600);

    update flight
    set progress = progress + 1, airplane_status = 'in_flight', next_time = addtime(next_time, flight_time)
    where flightID = ip_flightID;
end //
delimiter ;

-- [8] passengers_board
drop procedure if exists passengers_board;
delimiter //
create procedure passengers_board (in ip_flightID varchar(50))
sp_main: begin
    DECLARE v_cost INT;
    DECLARE v_progress INT;
    DECLARE v_current_airport CHAR(3);
    DECLARE v_next_airport CHAR(3);
    DECLARE v_airplane_location VARCHAR(50);
    DECLARE v_available_seats INT;
    DECLARE v_passenger_count INT;
    DECLARE v_current_airport_loc VARCHAR(50);
	if ip_flightID is null then
		leave sp_main;
	end if;
    IF ip_flightID NOT IN (
        SELECT flightID FROM flight WHERE airplane_status = 'on_ground'
    ) THEN
        LEAVE sp_main;
    END IF;
    
    SELECT progress, cost, support_airline, support_tail, routeID
      INTO v_progress, v_cost, @v_support_airline, @v_support_tail, @v_routeID
      FROM flight
     WHERE flightID = ip_flightID;
     
    if not exists (select 1 from route_path rp join flight f on rp.routeID = f.routeID where f.flightID = ip_flightID and rp.sequence > f.progress) then
        leave sp_main;
    end if;
    
    IF v_progress = 0 THEN
       SELECT l.departure INTO v_current_airport
         FROM route_path rp
         JOIN leg l ON rp.legID = l.legID
         WHERE rp.routeID = @v_routeID AND rp.sequence = 1;
       SELECT l.arrival INTO v_next_airport
         FROM route_path rp
         JOIN leg l ON rp.legID = l.legID
         WHERE rp.routeID = @v_routeID AND rp.sequence = 1;
    ELSE
       SELECT l.arrival INTO v_current_airport
         FROM route_path rp
         JOIN leg l ON rp.legID = l.legID
         WHERE rp.routeID = @v_routeID AND rp.sequence = v_progress;
       SELECT l.arrival INTO v_next_airport
         FROM route_path rp
         JOIN leg l ON rp.legID = l.legID
         WHERE rp.routeID = @v_routeID AND rp.sequence = v_progress + 1;
    END IF;
    
    SELECT a.locationID, a.seat_capacity
      INTO v_airplane_location, @v_seat_capacity
      FROM airplane a
      WHERE a.airlineID = @v_support_airline AND a.tail_num = @v_support_tail;
    
    SELECT COUNT(*) INTO @v_boarded
      FROM person
      WHERE locationID = v_airplane_location;
    SET v_available_seats = @v_seat_capacity - @v_boarded;
    
    SELECT locationID INTO v_current_airport_loc
      FROM airport
      WHERE airportID = v_current_airport;
    
    SELECT COUNT(*) INTO v_passenger_count
      FROM passenger pa
      JOIN person p ON pa.personID = p.personID
      JOIN passenger_vacations pv ON pa.personID = pv.personID
      WHERE p.locationID = v_current_airport_loc
        AND pv.airportID = v_next_airport
        AND pv.sequence = (
            SELECT MIN(sequence)
              FROM passenger_vacations
             WHERE personID = pa.personID
        )
        AND pa.funds >= v_cost;
    
    IF v_available_seats < v_passenger_count THEN
       LEAVE sp_main;
    END IF;
    
    UPDATE passenger pa
    JOIN person p ON pa.personID = p.personID
    JOIN passenger_vacations pv ON pa.personID = pv.personID
    SET p.locationID = v_airplane_location,
        pa.funds = pa.funds - v_cost
    WHERE p.locationID = v_current_airport_loc
      AND pv.airportID = v_next_airport
      AND pv.sequence = (
            SELECT MIN(sequence)
              FROM passenger_vacations
             WHERE personID = pa.personID
      )
      AND pa.funds >= v_cost;
end //
delimiter ;

-- [9] passengers_disembark
drop procedure if exists passengers_disembark;
delimiter //
create procedure passengers_disembark (in ip_flightID varchar(50))
sp_main: begin
    declare airplane_locID varchar(50);
    declare current_airport char(3);
    declare flight_route varchar(50);
    declare flight_progress integer;
    declare airport_locID varchar(50);
	if ip_flightID is null then
		leave sp_main;
	end if;
    if not exists (select 1 from flight where flightID = ip_flightID and airplane_status = 'on_ground') then
        leave sp_main;
    end if;
    
    select a.locationID, f.routeID, f.progress into airplane_locID, flight_route, flight_progress
    from flight f join airplane a on f.support_airline = a.airlineID and f.support_tail = a.tail_num
    where f.flightID = ip_flightID;
    
    select l.arrival into current_airport
    from route_path rp join leg l on rp.legID = l.legID
    where rp.routeID = flight_route and rp.sequence = flight_progress;
    
    select locationID into airport_locID from airport where airportID = current_airport;
    
    drop temporary table if exists temp_disembarking;
    create temporary table temp_disembarking (personID varchar(50) primary key);
    
    insert into temp_disembarking
    select p.personID
    from person p
    join passenger ps on p.personID = ps.personID
    join passenger_vacations pv on p.personID = pv.personID
    where p.locationID = airplane_locID  -- Were on this plane
    and pv.sequence = 1                 -- This was their next destination
    and pv.airportID = current_airport; -- Which matches current location
    
    update person p
    join temp_disembarking td on p.personID = td.personID
    set p.locationID = airport_locID;
    
    delete pv from passenger_vacations pv
    join temp_disembarking td on pv.personID = td.personID
    where pv.sequence = 1;
    
    update passenger_vacations pv
    join temp_disembarking td on pv.personID = td.personID
    set pv.sequence = pv.sequence - 1
    where pv.sequence > 1;
    
    drop temporary table temp_disembarking;
end //
delimiter ;

-- [10] assign_pilot
drop procedure if exists assign_pilot;
delimiter //
create procedure assign_pilot (in ip_flightID varchar(50), ip_personID varchar(50))
sp_main: begin
    DECLARE airplane_type VARCHAR(50);
    DECLARE airplane_locID VARCHAR(50);
    DECLARE pilot_locID VARCHAR(50);
    DECLARE departure_airport CHAR(3);
    DECLARE airport_locID VARCHAR(50);
    DECLARE max_seq INTEGER;
    DECLARE has_general_license BOOLEAN DEFAULT false;
	if ip_flightID is null then
		leave sp_main;
	end if;
	if ip_personID is null then
		leave sp_main;
	end if;
    IF NOT EXISTS (SELECT 1 FROM flight WHERE flightID = ip_flightID AND airplane_status = 'on_ground') THEN
        LEAVE sp_main;
    END IF;

    SELECT MAX(sequence) INTO max_seq
      FROM route_path
     WHERE routeID = (SELECT routeID FROM flight WHERE flightID = ip_flightID);
     
    IF (SELECT progress FROM flight WHERE flightID = ip_flightID) >= max_seq THEN
        LEAVE sp_main;
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pilot WHERE personID = ip_personID AND commanding_flight IS NULL) THEN
        LEAVE sp_main;
    END IF;

    SELECT a.plane_type INTO airplane_type
      FROM flight f
      JOIN airplane a ON f.support_airline = a.airlineID AND f.support_tail = a.tail_num
     WHERE f.flightID = ip_flightID;

    SELECT l.departure INTO departure_airport
      FROM route_path rp
      JOIN leg l ON rp.legID = l.legID
     WHERE rp.routeID = (SELECT routeID FROM flight WHERE flightID = ip_flightID)
       AND rp.sequence = ((SELECT progress FROM flight WHERE flightID = ip_flightID) + 1);

    SELECT locationID INTO airport_locID
      FROM airport
     WHERE airportID = departure_airport;

    SELECT locationID INTO pilot_locID
      FROM person
     WHERE personID = ip_personID;

    SELECT EXISTS (
             SELECT 1 FROM pilot_licenses
              WHERE personID = ip_personID AND license = 'general'
           ) INTO has_general_license;

    IF NOT (
          (airplane_type IS NULL AND has_general_license)
       OR EXISTS (SELECT 1 FROM pilot_licenses WHERE personID = ip_personID AND license = airplane_type)
    ) THEN
        LEAVE sp_main;
    END IF;

    IF pilot_locID <> airport_locID THEN
        LEAVE sp_main;
    END IF;

    UPDATE pilot
       SET commanding_flight = ip_flightID
     WHERE personID = ip_personID;

    UPDATE person
       SET locationID = (
           SELECT a.locationID
             FROM airplane a
             JOIN flight f ON a.airlineID = f.support_airline AND a.tail_num = f.support_tail
            WHERE f.flightID = ip_flightID
       )
     WHERE personID = ip_personID;
end //
delimiter ;

-- [11] recycle_crew
drop procedure if exists recycle_crew;
delimiter //
create procedure recycle_crew (in ip_flightID varchar(50))
sp_main: begin
    declare v_airport_location varchar(50);
	if ip_flightID is null then
		leave sp_main;
	end if;
    if ip_flightID not in (
        select f.flightID 
        from flight f
        where f.airplane_status = 'on_ground'
          and f.progress >= (select count(*) from route_path where routeID = f.routeID)
    ) then
        leave sp_main;
    end if;
    
    if exists (
        select 1 
        from passenger pa
        join person p on pa.personID = p.personID
        join airplane a on p.locationID = a.locationID
        join flight f on f.support_airline = a.airlineID and f.support_tail = a.tail_num
        where f.flightID = ip_flightID
    ) then
        leave sp_main;
    end if;
    
    select a.locationID into v_airport_location
    from airport a
    where a.airportID = (
         select l.arrival
         from flight f
         join route_path rp on f.routeID = rp.routeID
         join leg l on rp.legID = l.legID
         where f.flightID = ip_flightID
           and rp.sequence = f.progress
    );
    
    update pilot p
    join person pe on p.personID = pe.personID
    set p.commanding_flight = null,
        pe.locationID = v_airport_location
    where p.commanding_flight = ip_flightID;
end //
delimiter ;

-- [12] retire_flight
drop procedure if exists retire_flight;
delimiter //
create procedure retire_flight (in ip_flightID varchar(50))
sp_main: begin
	if ip_flightID is null then
		leave sp_main;
	end if;
    if ip_flightID not in (
        select f.flightID
        from flight f
        where f.airplane_status = 'on_ground'
        and (f.progress = 0 or f.progress >= (
            select count(*) from route_path where routeID = f.routeID
        ))
    ) then
        leave sp_main;
    end if;
    
    if exists (
        select 1 from person p
        join airplane a on p.locationID = a.locationID
        join flight f on f.support_airline = a.airlineID 
            and f.support_tail = a.tail_num
        where f.flightID = ip_flightID
    ) then
        leave sp_main;
    end if;
    
    delete from flight where flightID = ip_flightID;
end //
delimiter ;

-- [13] simulation_cycle
drop procedure if exists simulation_cycle;
delimiter //
create procedure simulation_cycle ()
sp_main: begin
    declare v_flightID varchar(50);
    declare v_status varchar(100);
    declare v_progress integer;
    declare v_route_length integer;
    
    select f.flightID, f.airplane_status, f.progress,
           (select count(*) from route_path where routeID = f.routeID) as route_length
    into v_flightID, v_status, v_progress, v_route_length
    from flight f
    order by f.next_time asc, 
             case when f.airplane_status = 'in_flight' then 0 else 1 end,
             f.flightID
    limit 1;
    if v_flightID is null then
		leave sp_main;
	end if;
    if v_status = 'in_flight' then
        call flight_landing(v_flightID);
        call passengers_disembark(v_flightID);
        
        if v_progress >= v_route_length then
            call recycle_crew(v_flightID);
            call retire_flight(v_flightID);
        end if;
    else
		if v_progress >= v_route_length then
            call recycle_crew(v_flightID);
            call retire_flight(v_flightID);
		else
        call passengers_board(v_flightID);
        call flight_takeoff(v_flightID);
        end if;
    end if;
end //
delimiter ;

-- [14] flights_in_the_air
create or replace view flights_in_the_air (departing_from, arriving_at, num_flights,
    flight_list, earliest_arrival, latest_arrival, airplane_list) as
SELECT 
    l.departure,
    l.arrival,
    COUNT(f.flightID),
    GROUP_CONCAT(f.flightID ORDER BY f.flightID),
    MIN(f.next_time),
    MAX(f.next_time),
    GROUP_CONCAT(a.locationID ORDER BY f.flightID)
FROM flight f
JOIN route_path rp ON f.routeID = rp.routeID
JOIN leg l ON rp.legID = l.legID
JOIN airplane a ON f.support_airline = a.airlineID AND f.support_tail = a.tail_num
WHERE f.airplane_status = 'in_flight'
  AND rp.sequence = f.progress
GROUP BY l.departure, l.arrival;

-- [15] flights_on_the_ground
create or replace view flights_on_the_ground (departing_from, num_flights,
    flight_list, earliest_arrival, latest_arrival, airplane_list) as 
SELECT 
    CASE 
       WHEN f.progress = 0 THEN l.departure
       ELSE l.arrival
    END AS departing_from,
    COUNT(f.flightID) AS num_flights,
    GROUP_CONCAT(f.flightID ORDER BY f.flightID) AS flight_list,
    MIN(f.next_time) AS earliest_arrival,
    MAX(f.next_time) AS latest_arrival,
    GROUP_CONCAT(a.locationID ORDER BY f.flightID) AS airplane_list
FROM flight f
JOIN route_path rp 
  ON f.routeID = rp.routeID 
  AND rp.sequence = (CASE WHEN f.progress = 0 THEN 1 ELSE f.progress END)
JOIN leg l 
  ON rp.legID = l.legID
JOIN airplane a 
  ON f.support_airline = a.airlineID 
  AND f.support_tail = a.tail_num
WHERE f.airplane_status = 'on_ground'
GROUP BY departing_from;


-- [16] people_in_the_air
create or replace view people_in_the_air (departing_from, arriving_at, num_airplanes,
    airplane_list, flight_list, earliest_arrival, latest_arrival, num_pilots,
    num_passengers, joint_pilots_passengers, person_list) as
select 
    l.departure,
    l.arrival,
    count(distinct a.locationID),
    group_concat(distinct a.locationID order by a.locationID separator ', '),
    group_concat(distinct f.flightID order by f.flightID separator ', '),
    min(f.next_time),
    max(f.next_time),
    sum(case when pl.personID is not null then 1 else 0 end),
    sum(case when ps.personID is not null then 1 else 0 end),
    count(distinct p.personID),
    group_concat(distinct p.personID order by p.personID separator ', ')
from 
    person p
    left join pilot pl on p.personID = pl.personID
    left join passenger ps on p.personID = ps.personID
    join airplane a on p.locationID = a.locationID
    join flight f on a.airlineID = f.support_airline and a.tail_num = f.support_tail
    join route_path rp on f.routeID = rp.routeID and rp.sequence = f.progress
    join leg l on rp.legID = l.legID
where 
    f.airplane_status = 'in_flight'
group by 
    l.departure, l.arrival;

-- [17] people_on_the_ground
create or replace view people_on_the_ground (departing_from, airport, airport_name, 
	city, state, country, num_pilots, num_passengers, joint_pilots_passengers, person_list) as
select 
    a.airportID as departing_from,
    a.locationID as airport,
    a.airport_name,
    a.city,
    a.state,
    a.country,
    count(distinct pi.personID) as num_pilots,
    count(distinct pa.personID) as num_passengers,
    count(distinct p.personID) as joint_pilots_passengers,
    group_concat(distinct p.personID order by p.personID) as person_list
from airport a
join person p on p.locationID = a.locationID
left join pilot pi on p.personID = pi.personID
left join passenger pa on p.personID = pa.personID
group by a.airportID, a.locationID, a.airport_name, a.city, a.state, a.country;

-- [18] route_summary
create or replace view route_summary (route, num_legs, leg_sequence, route_length,
    num_flights, flight_list, airport_sequence) as
select
    r.routeID as route,
    count(rp.legID) as num_legs,
    group_concat(rp.legID order by rp.sequence) as leg_sequence,
    sum(l.distance) as route_length,
    (select count(*) from flight f where f.routeID = r.routeID) as num_flights,
    (select group_concat(f.flightID) from flight f where f.routeID = r.routeID) as flight_list,
	group_concat(distinct concat(l.departure, '->', l.arrival) order by rp.sequence separator ', ')
from
    route r
join
    route_path rp on r.routeID = rp.routeID
join
    leg l on rp.legID = l.legID
group by
    r.routeID;


-- [19] alternative_airports
create or replace view alternative_airports (city, state, country, num_airports,
    airport_code_list, airport_name_list) as
select 
    a.city,
    a.state,
    a.country,
    count(distinct a.airportID) as num_airports,
    group_concat(distinct a.airportID order by a.airportID) as airport_code_list,
    group_concat(distinct a.airport_name order by a.airportID) as airport_name_list
from airport a
group by a.city, a.state, a.country
having count(distinct a.airportID) > 1;
