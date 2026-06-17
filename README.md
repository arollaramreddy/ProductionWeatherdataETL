# Production Weather Data ETL

Containerized weather analytics pipeline built with Python, PostgreSQL, Airflow, dbt, Docker Compose, and Apache Superset.

The pipeline extracts current weather data from the Weatherstack API, loads raw observations into PostgreSQL, transforms them into tested dbt silver/gold models, orchestrates the workflow with Airflow, and exposes dashboard-ready tables through Superset.

## Architecture

```text
Weatherstack API
      |
      v
Python ingestion
      |
      v
PostgreSQL
  weatherstack.weather_data
      |
      v
dbt
  weatherstack.silver
  weatherstack.gold
      |
      v
Apache Superset
```

Airflow schedules the ingestion and dbt transformation workflow. Docker Compose runs the local platform.

## Features

- API extraction with configurable city, timeout, and mock mode
- PostgreSQL schema/table creation and indexed raw weather storage
- Airflow DAGs for ingestion-only and ingestion-plus-dbt workflows
- dbt source freshness, column tests, de-duplication, and daily aggregates
- Superset service backed by Postgres metadata and Redis cache
- Local secret handling through untracked `.env` files
- Portable Docker Compose setup without machine-specific host paths

## Tech Stack

| Layer | Tool |
| --- | --- |
| Extraction | Python, Requests, Weatherstack API |
| Storage | PostgreSQL 17 |
| Orchestration | Apache Airflow 3 |
| Transformation | dbt Postgres |
| Visualization | Apache Superset |
| Runtime | Docker Compose |

## Repository Structure

```text
repos/
  api_request/
    api_requests.py        Weatherstack API client and mock payload
    insert_data.py         Postgres table creation and weather insert logic

  airflow/
    Dockerfile             Airflow image with dbt and ETL dependencies
    requirements.txt
    dags/
      orchestrator.py      Ingestion-only DAG
      dbt_orchestrator.py  Ingestion plus dbt DAG

  dbt/
    profiles.yml
    weather_project/
      dbt_project.yml
      models/
        sources/sources.yml
        silver/silver.sql
        gold/gold.sql
        schema.yml

  postgres/
    init_metadata.sh       Creates Airflow and Superset metadata databases

  superset/
    Dockerfile
    superset_config.py

  docker-compose.yaml
```

## Prerequisites

- Docker Desktop
- Docker Compose
- Weatherstack API key for live ingestion
- Python 3.13 only if running the ingestion script outside Docker

## Environment Setup

Create the platform environment file:

```bash
cd repos
cp .env.example .env
```

Edit `repos/.env` and set local passwords. The key values are:

```env
POSTGRES_DB=weather_db
POSTGRES_USER=your_postgres_user
POSTGRES_PASSWORD=change_me_postgres_password
WEATHER_CITY=New York
USE_MOCK_WEATHER=false
```

Create the Weatherstack API file:

```bash
cp api_request/.env.example api_request/.env
```

Set:

```env
API_KEY=your_weatherstack_api_key
```

For a demo without a live API key, set this in `repos/.env`:

```env
USE_MOCK_WEATHER=true
```

`.env` files are intentionally ignored by Git.

## Run The Platform

From `repos/`:

```bash
docker compose up -d --build
```

Service URLs:

| Service | URL |
| --- | --- |
| Airflow | `http://localhost:8000` |
| Superset | `http://localhost:8088` |
| Postgres | `localhost:5001` |

Check containers:

```bash
docker compose ps
```

Stop the stack:

```bash
docker compose down
```

## Airflow DAGs

The project includes two DAGs:

| DAG | Purpose |
| --- | --- |
| `extract_weather_data` | Fetches current weather and inserts it into Postgres. |
| `dbt_orchestrator` | Fetches current weather, then runs dbt models. |

Both DAGs use `WEATHER_INGEST_INTERVAL_MINUTES` from `repos/.env` and default to every 5 minutes.

## Run Ingestion Manually

Start Postgres:

```bash
cd repos
docker compose up -d database
```

From the repository root, run:

```bash
uv run python repos/api_request/insert_data.py
```

Equivalent root entry point:

```bash
uv run python main.py
```

The script creates `weatherstack.weather_data` if it does not exist, then inserts one weather observation.

## Run dbt Manually

From `repos/`:

```bash
docker compose --profile manual run --rm dbt debug
docker compose --profile manual run --rm dbt run
docker compose --profile manual run --rm dbt test
docker compose --profile manual run --rm dbt source freshness
```

dbt models:

| Model | Description |
| --- | --- |
| `silver` | De-duplicates raw weather observations by city and local observation time. |
| `gold` | Produces daily city-level aggregates for dashboards. |

## Query Postgres

Open psql:

```bash
docker exec -it postgres_container psql -U <POSTGRES_USER> -d weather_db
```

Useful queries:

```sql
\dt weatherstack.*
select * from weatherstack.weather_data order by inserted_at desc limit 10;
select * from weatherstack.silver order by weather_time_local desc limit 10;
select * from weatherstack.gold order by weather_date desc limit 10;
```

## Connect Superset

Superset runs at:

```text
http://localhost:8088
```

Use the admin credentials from `repos/.env`.

Add the analytics database in Superset:

```text
Database type: PostgreSQL
Host: database
Port: 5432
Database: weather_db
Username: POSTGRES_USER from repos/.env
Password: POSTGRES_PASSWORD from repos/.env
```

SQLAlchemy URI format:

```text
postgresql+psycopg2://<POSTGRES_USER>:<POSTGRES_PASSWORD>@database:5432/<POSTGRES_DB>
```

Recommended datasets:

```text
weatherstack.weather_data
weatherstack.silver
weatherstack.gold
```

## Common Commands

```bash
cd repos
docker compose up -d --build
docker compose logs -f airflow
docker compose logs -f database
docker compose logs -f superset
docker compose down --remove-orphans
```

## Production Readiness Notes

This is a local production-style project, not a full cloud production deployment. In a real deployment, the next steps would be:

- Move secrets to AWS Secrets Manager, GCP Secret Manager, Vault, or Kubernetes Secrets
- Use managed Postgres or a cloud warehouse for analytics storage
- Split Airflow into webserver, scheduler, workers, triggerer, and metadata database services
- Run dbt through Airflow workers, KubernetesPodOperator, or dbt Cloud
- Add CI checks for Python linting, dbt compile/test, and Docker builds
- Add observability with logs, metrics, alerts, and data freshness monitoring
- Version Superset dashboards as importable assets
- Add multi-city ingestion and incremental dbt models

## Project Summary

This project provides a local, containerized weather data ETL and analytics stack. It is designed for repeatable development with Docker Compose and keeps ingestion, transformation, orchestration, storage, and visualization concerns separated across dedicated services.
