class Config:
    # Database configuration - Make sure to update this stuff so that it is your actual MySQL login from class
    DB_HOST = 'localhost'
    DB_USER = 'root'
    DB_PASSWORD = 'mysql123'
    DB_NAME = 'flight_tracking'
    
    # Flask configuration
    SECRET_KEY = 'dev'  # Change this in production
    
    @classmethod
    def get_db_config(cls):
        return {
            'host': cls.DB_HOST,
            'user': cls.DB_USER,
            'password': cls.DB_PASSWORD,
            'database': cls.DB_NAME
        } 