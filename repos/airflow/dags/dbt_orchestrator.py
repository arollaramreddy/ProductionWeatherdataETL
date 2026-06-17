import os
import sys
from datetime import datetime, timedelta

from airflow.providers.standard.operators.bash import BashOperator
from airflow.sdk import dag, task

sys.path.append("/opt/airflow/api_request")
from insert_data import main

DBT_PROJECT_PATH = "/opt/airflow/dbt/weather_project"
DBT_PROFILES_PATH = "/opt/airflow/dbt"

default_args = {
    "description": "Extract weather data and build dbt analytics models",
    "retries": 2,
    "retry_delay": timedelta(minutes=2),
}


@dag(
    dag_id="dbt_orchestrator",
    default_args=default_args,
    start_date=datetime(2026, 5, 12),
    schedule=timedelta(minutes=int(os.getenv("WEATHER_INGEST_INTERVAL_MINUTES", "5"))),
    catchup=False,
    tags=["weather", "dbt", "analytics"],
)
def weather_analytics_pipeline():
    @task
    def insert_weather_data():
        main()

    transform_weather_models = BashOperator(
        task_id="transform_weather_models",
        bash_command=(
            f"dbt run --project-dir {DBT_PROJECT_PATH} "
            f"--profiles-dir {DBT_PROFILES_PATH}"
        ),
        append_env=True,
    )

    insert_weather_data() >> transform_weather_models


weather_analytics_pipeline()
