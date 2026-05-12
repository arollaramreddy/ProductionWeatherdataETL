from api_requests import mock_fetch_data
import psycopg2

#function for connection to postgres database
def connect_database():
    try:
        print("connecting to database started......")
        conn=psycopg2.connect(
            host="localhost",
            port=5001,
            dbname="weather_db",
            user="arollaramreddy",
            password="weather_db_password"
        )
        
        return conn
    
    except psycopg2.Error as e:
        print(f"Database connection failed: {e}")
        
connect_database()
        