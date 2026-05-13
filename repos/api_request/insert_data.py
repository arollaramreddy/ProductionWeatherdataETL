import os
from pathlib import Path

import psycopg2
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR.parent / ".env")
load_dotenv(BASE_DIR / ".env")

from api_requests import api_url, fetch_data, mock_fetch_data


def get_env(*names):
    for name in names:
        value = os.getenv(name)
        if value:
            return value
    raise RuntimeError(f"Missing required environment variable. Tried: {', '.join(names)}")

#function for connection to postgres database
def connect_database():
    try:
        print("connecting to database started......")
        conn=psycopg2.connect(
            host=os.getenv("DB_HOST", "localhost"),
            port=os.getenv("DB_PORT", os.getenv("POSTGRES_HOST_PORT", "5001")),
            dbname=get_env("DB_NAME", "POSTGRES_DB"),
            user=get_env("DB_USER", "POSTGRES_USER"),
            password=get_env("DB_PASSWORD", "POSTGRES_PASSWORD")
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
    try:
        #data=mock_fetch_data()
        data=fetch_data(api_url)
        conn=connect_database()

        if conn:
            create_table(conn)
            insert_data(conn, data)
        else:
            print("Database connection failed. Stopping script.")
    except Exception as e:
        print(f"An error occured during execution: {e}")
    finally:
        if 'conn' in locals():
            conn.close()
            print("Database connection closed")
        

if __name__ == "__main__":
    main()
