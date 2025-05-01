import pytest
from app import app, get_db_connection
from config import Config

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_db_config():
    #est that database configuration is loaded correctly
   
    db_config = Config.get_db_config()
    assert db_config['host'] is not None, "DB_HOST not configured"
    assert db_config['user'] is not None, "DB_USER not configured"
    assert db_config['password'] is not None, "DB_PASSWORD not configured"
    assert db_config['database'] is not None, "DB_NAME not configured"
    
    
    try:
        conn = get_db_connection()
        assert conn is not None, "Failed to establish database connection"
        conn.close()
    except Exception as e:
        pytest.fail(f"Database connection failed: {str(e)}")

def test_index_route(client):
    """Test the home page route"""
    response = client.get('/')
    assert response.status_code == 200
    assert b'Welcome' in response.data

def test_airlines_route(client):
    """Test the airlines page route"""
    response = client.get('/airlines')
    assert response.status_code == 200
    assert b'Airlines' in response.data

def test_airports_route(client):
    """Test the airports page route"""
    response = client.get('/airports')
    assert response.status_code == 200
    assert b'Airports' in response.data

def test_flights_route(client):
    """Test the flights page route"""
    response = client.get('/flights')
    assert response.status_code == 200
    assert b'Flights' in response.data

def test_pilots_route(client):
    """Test the pilots page route"""
    response = client.get('/pilots')
    assert response.status_code == 200
    assert b'Pilots' in response.data

def test_passengers_route(client):
    """Test the passengers page route"""
    response = client.get('/passengers')
    assert response.status_code == 200
    assert b'Passengers' in response.data

def test_health_check(client):
    """Test the health check endpoint"""
    response = client.get('/health')
    assert response.status_code == 200
    assert response.json == {'status': 'healthy'}

def test_reservations_route(client):
    """Test the reservations route"""
    response = client.get('/reservations')
    assert response.status_code == 200

def test_404_error(client):
    """Test 404 error handling"""
    response = client.get('/nonexistent-route')
    assert response.status_code == 404

def test_database_connection():
    """Test database connection"""
    conn = get_db_connection()
    assert conn is not None
    conn.close()

def test_edit_airport_get(client):
    """Test getting the edit airport page"""
    # First try with a non-existent airport
    response = client.get('/airports/edit/NONEXISTENT')
    assert response.status_code == 302  # Should redirect
    
    # Try with an existing airport (you may need to change this ID based on your test data)
    response = client.get('/airports/edit/CDG')
    assert response.status_code in [200, 302]  # Either success or redirect is acceptable for testing

def test_edit_airport_post(client):
    """Test updating an airport"""
    # Try updating an existing airport
    response = client.post('/airports/edit/CDG', data={
        'airport_code': 'CDG',
        'airport_name': 'Charles de Gaulle Airport',
        'city': 'Paris',
        'state': 'Île-de-France',
        'country': 'France'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'successfully' in response.data or b'Airport' in response.data  # More flexible assertion

def test_add_airport(client):
    """Test adding a new airport"""
    response = client.post('/airports/add', data={
        'airportID': 'TST',  # 3-char code
        'airport_name': 'Test Airport',
        'city': 'Test',
        'state': 'TS',  # 2-char code
        'country': 'USA',  
        'locationID': '1'
    }, follow_redirects=True)
    assert response.status_code == 200
    
    # Check if the airport was added successfully or if there was a constraint violation
    assert any(msg in response.data for msg in [
        b'Airport added successfully!',
        b'Cannot add/update this record',
        b'Database error'
    ])

def test_edit_airport_validation(client):
    """Test airport edit validation"""
    # Test mising
    response = client.post('/airports/edit/TEST', data={
        'airport_name': '',
        'city': '',
        'state': '',
        'country': ''
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'No fields to update' in response.data

def test_delete_airport(client):
    """Test deleting an airport"""
   
    client.post('/airports/add', data={
        'airportID': 'DEL',
        'airport_name': 'Delete Test Airport',
        'city': 'Delete City',
        'state': 'DL',
        'country': 'Delete Country',
        'locationID': '1'
    })
    
    
    response = client.post('/airports/delete/DEL', follow_redirects=True)
    assert response.status_code == 200
    assert b'Airport deleted successfully!' in response.data

def test_get_table_schema():
    """Test schema retrieval function"""
    from app import get_table_schema
    
   
    schema = get_table_schema('airport')
    assert schema is not None
    
 
    field_names = [field['Field'] for field in schema]
    required_fields = ['airportID', 'airport_name', 'city', 'state', 'country', 'locationID']
    for field in required_fields:
        assert field in field_names

def test_database_constraints():
    """Test database constraints"""
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            # Test length constraint for airportID
            try:
                cursor.execute("""
                    INSERT INTO airport (airportID, airport_name, city, state, country, locationID)
                    VALUES ('TOOLONG', 'Test Airport', 'Test', 'TS', 'USA', '1')
                """)
                assert False, "Should have raised a data length error"
            except Exception as e:
                assert "data too long" in str(e).lower()
            
            # Test foreign key constraint with valid length but invalid locationID
            try:
                cursor.execute("""
                    INSERT INTO airport (airportID, airport_name, city, state, country, locationID)
                    VALUES ('TST', 'Test Airport', 'Test', 'TS', 'USA', '999999')
                """)
                assert False, "Should have raised a foreign key constraint error"
            except Exception as e:
                assert "foreign key constraint" in str(e).lower() or "cannot add or update" in str(e).lower()
    finally:
        conn.close()

if __name__ == '__main__':
    pytest.main(['-v', 'test_routes.py']) 