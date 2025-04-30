from app import get_db_connection, app
import traceback

with app.app_context():
    try:
        conn = get_db_connection()
        print('Database connection successful!')
        conn.close()
    except Exception as e:
        print(f'Error: {e}')
        traceback.print_exc() 