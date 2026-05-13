from api_requests import mock_fetch_data
import os
import psycopg2

#function for connection to postgres database
def connect_database():
    try:
        print("connecting to database started......")
        conn=psycopg2.connect(
            host=os.getenv("DB_HOST", "localhost"),
            port=os.getenv("DB_PORT", "5001"),
            dbname=os.getenv("DB_NAME", "weather_db"),
            user=os.getenv("DB_USER", "arollaramreddy"),
            password=os.getenv("DB_PASSWORD", "weather_db_password")
        )
        print("connection to database successfull")
        return conn
    
    except psycopg2.Error as e:
        print(f"Database connection failed: {e}")
        
#function for creating table if not exists
def create_table(conn):
    try:
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
        return cur
        
    except psycopg2.Error as e:
        print(f"Falied to create table : {e}")
        
#create_table()

#create function to insert data
def insert_data(conn,data):
    try:
        print("Inserting weather data........")
        cur=conn.cursor()
        cur.execute('''insert into weatherstack.weather_data(city,temperature,weather_description,wind_speed,time,inserted_at,utc_offset) values(%s,%s,%s,%s,%s, NOW(),%s)''',
                        (
                            data['location']['name'],
                            data['current']['temperature'],
                            data['current']['weather_descriptions'][0],
                            data['current']['wind_speed'],
                            data['location']['localtime'],
                            data['location']['utc_offset']
                        )
                    )
        conn.commit()
        print("Data inserted successfully")
        
    except psycopg2.Error as e:
        print(f"Failed to insert data: {e}")
def main():
    data=mock_fetch_data()
    conn=connect_database()

    if conn:
        create_table(conn)
        insert_data(conn, data)
        conn.close()
    else:
        print("Database connection failed. Stopping script.")


if __name__ == "__main__":
    main()
