import sys
import os
from datetime import datetime, timedelta

from airflow.sdk import dag, task
from airflow.providers.docker.operators.docker import DockerOperator
from docker.types import Mount

sys.path.append("/opt/airflow/api_request")
from insert_data import main

DBT_PROJECT_PATH = (
    os.environ.get("DBT_PROJECT_HOST_PATH")
    or "/absolute/path/to/ProductionWeatherdataETL/repos/dbt/weather_project"
)
DBT_PROFILES_PATH = (
    os.environ.get("DBT_PROFILES_HOST_PATH")
    or "/absolute/path/to/ProductionWeatherdataETL/repos/dbt"
)
DBT_DOCKER_NETWORK = os.environ.get("DBT_DOCKER_NETWORK") or "repos_my_network"


default_args={
    'description': 'A DAG to orchestrate data',
    'start_date': datetime(2026, 5, 12),
    'catchup':False
}

@dag(
    dag_id="dbt_orchestrator",
    default_args=default_args,
    schedule=timedelta(minutes=5)
)
def extract_weather_data():
    @task
    def insert_weather_data():
        main()

    transform_data = DockerOperator(
        task_id="transform_data",
        image="ghcr.io/dbt-labs/dbt-postgres:1.9.latest",
        command="run",
        working_dir="/usr/app",
        mounts=[
            Mount(source=DBT_PROJECT_PATH, target="/usr/app", type="bind"),
            Mount(source=DBT_PROFILES_PATH, target="/root/.dbt", type="bind"),
        ],
        network_mode=DBT_DOCKER_NETWORK,
        docker_url="unix://var/run/docker.sock",
        auto_remove="success",
        mount_tmp_dir=False,
        environment={
            "DB_HOST": "database",
            "DB_PORT": "5432",
            "DB_NAME": os.environ["DB_NAME"],
            "DB_USER": os.environ["DB_USER"],
            "DB_PASSWORD": os.environ["DB_PASSWORD"],
        },
    )
    
    
    insert_weather_data() >> transform_data

extract_weather_data()
