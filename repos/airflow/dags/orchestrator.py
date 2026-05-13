import sys
from datetime import datetime, timedelta

from airflow.sdk import dag, task

sys.path.append("/opt/airflow/api_request")
from insert_data import main

default_args={
    'description': 'A DAG to extract weather data and load it into Postgres',
    'start_date': datetime(2026, 5, 12),
    'catchup':False
}

@dag(
    dag_id="extract_weather_data",
    default_args=default_args,
    schedule=timedelta(minutes=5)
)
def extract_weather_data():
    @task
    def insert_weather_data():
        main()
        
    insert_weather_data()

extract_weather_data()
