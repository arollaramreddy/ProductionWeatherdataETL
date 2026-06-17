import os
import sys
from datetime import datetime, timedelta

from airflow.sdk import dag, task

sys.path.append("/opt/airflow/api_request")
from insert_data import main

default_args = {
    "description": "Extract current weather data and load it into Postgres",
    "retries": 2,
    "retry_delay": timedelta(minutes=2),
}


@dag(
    dag_id="extract_weather_data",
    default_args=default_args,
    start_date=datetime(2026, 5, 12),
    schedule=timedelta(minutes=int(os.getenv("WEATHER_INGEST_INTERVAL_MINUTES", "5"))),
    catchup=False,
    tags=["weather", "etl"],
)
def extract_weather_data():
    @task
    def insert_weather_data():
        main()

    insert_weather_data()


extract_weather_data()
