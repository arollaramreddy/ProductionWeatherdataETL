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
        print("connection to database successfull")
        return conn
    
    except psycopg2.Error as e:
        print(f"Database connection failed: {e}")
        
#function for creating table if not exists
def create_table():
    try:
        conn=connect_database()
        print("creating table......")
        cur=conn.cursor()
        cur.execute('''
                    create schema if not exists weatherstack;
                    create table if not exists weatherstack.weather_data(
                        id serial,
                        city varchar(20),
                        temperature float,
                        weather_description text,
                        wind_speed float,
                        time Timestamp,
                        inserted_at Timestamp default NOW(),
                        utc_offset text,
                        primary key(id)
                    );
                    ''')
        
        conn.commit()
        print("table created successfully")
        
    except psycopg2.Error as e:
        print(f"Falied to create table : {e}")
        
create_table()