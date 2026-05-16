# ProductionWeatherdataETL

Containerized weather data pipeline using Python, Postgres, Airflow, dbt, and Apache Superset.

This project is a production-style data engineering stack. It extracts weather data from the Weatherstack API, loads it into Postgres, transforms it with dbt, orchestrates jobs with Airflow, and exposes the final tables for visualization in Superset.

## Architecture

```text
Weatherstack API
      |
      v
Python ETL scripts
      |
      v
Postgres database
  - weatherstack.weather_data
      |
      v
dbt transformations
  - bronze
  - silver/gold models
      |
      v
Apache Superset dashboards

Airflow orchestrates the ETL and dbt workflow.
Docker Compose runs the local platform.
```

## Services

The main Compose file is:

```text
repos/docker-compose.yaml
```

It defines these services:

```text
database       Postgres 17 database for weather data, Airflow metadata, and Superset metadata
airflow        Airflow 3 standalone instance for orchestration
dbt            dbt Postgres container for transformations
redis          Redis cache used by Superset
superset-init  One-time Superset metadata migration/admin initialization
superset       Superset web application for visualization
```

Default ports:

```text
Postgres:  localhost:5001 -> container:5432
Airflow:   http://localhost:8000
Superset:  http://localhost:8088
```

## Project Structure

```text
repos/
  api_request/
    api_requests.py       Fetches weather data
    insert_data.py        Creates table and inserts weather data into Postgres

  airflow/
    dags/
      orchestrator.py       Airflow DAG for Python ETL
      dbt_orchestrator.py   Airflow DAG for dbt transformations

  dbt/
    profiles.yml
    weather_project/
      dbt_project.yml
      models/
        sources/
          sources.yml
        bronze/
          bronze.sql
        gold/
          gold.sql

  postgres/
    init_metadata.sh      Creates Airflow and Superset metadata databases/users

  superset/
    Dockerfile
    superset_config.py

  docker-compose.yaml
```

## Important Concepts

### ETL

ETL stands for Extract, Transform, Load.

In this project:

```text
Extract:   Python fetches weather data from Weatherstack
Load:      Python inserts raw data into Postgres
Transform: dbt creates clean analytics models
Visualize: Superset reads transformed tables
```

### Postgres

Postgres stores the weather data and metadata for platform services.

Main weather database:

```text
database: weather_db
schema:   weatherstack
table:    weather_data
```

Inside Docker containers, the Postgres host is:

```text
database
```

From your laptop, the Postgres host is:

```text
localhost
```

with port:

```text
5001
```

### Airflow

Airflow schedules and orchestrates the pipeline. It controls the order of tasks such as:

```text
insert weather data -> run dbt transformations
```

The current setup uses `airflow standalone`, which is good for local development. In production, Airflow is usually split into webserver, scheduler, workers, triggerer, and metadata database services.

### dbt

dbt manages SQL transformations. It reads source data from Postgres and creates modeled tables.

Example source:

```text
weatherstack.weather_data
```

Example model:

```text
weatherstack.bronze
```

dbt config files:

```text
repos/dbt/profiles.yml
repos/dbt/weather_project/dbt_project.yml
repos/dbt/weather_project/models/sources/sources.yml
```

### Superset

Superset is the BI and visualization layer. It connects to Postgres and allows dashboards, charts, SQL exploration, and reporting.

Superset app:

```text
http://localhost:8088
```

Default local login from `repos/.env`:

```text
username: admin
password: admin
```

For real production, change these credentials and the `SUPERSET_SECRET_KEY` in your real `.env` file.

## Prerequisites

Install:

```text
Docker Desktop
Docker Compose
Python 3.12 or later, optional for local script execution
```

Create the platform environment file:

```bash
cd repos
cp .env.example .env
```

Then edit `repos/.env` and set real local secrets/passwords.

Create your Weatherstack API key file:

```text
repos/api_request/.env
```

You can start from the example file:

```bash
cp repos/api_request/.env.example repos/api_request/.env
```

Example:

```env
API_KEY=your_weatherstack_api_key
```

Do not commit `.env` files to Git.

## How To Run

From the repository root:

```bash
cd repos
docker compose up -d --build
```

Check services:

```bash
docker compose ps
```

Open Airflow:

```text
http://localhost:8000
```

Open Superset:

```text
http://localhost:8088
```

## Running The Python ETL Manually

Start Postgres:

```bash
cd repos
docker compose up -d database
```

Run the insert script from the API folder:

```bash
cd api_request
python insert_data.py
```

This creates the schema/table if needed and inserts weather data.

## Running dbt Manually

From `repos/`:

```bash
docker compose run --rm dbt debug
```

Run all dbt models:

```bash
docker compose run --rm dbt run
```

Run only the bronze model:

```bash
docker compose run --rm dbt run --select bronze
```

## Checking Postgres

Open a Postgres shell:

```bash
docker exec -it postgres_container psql -U arollaramreddy -d weather_db
```

List tables:

```sql
\dt weatherstack.*
```

Query raw data:

```sql
select * from weatherstack.weather_data;
```

Query dbt model:

```sql
select * from weatherstack.bronze;
```

Exit:

```sql
\q
```

## Connecting Superset To Weather Data

Superset uses its own metadata database, but you still need to add `weather_db` as an analytics database inside the Superset UI.

In Superset:

```text
Settings -> Database Connections -> + Database
```

Use:

```text
Database type: PostgreSQL
Host: database
Port: 5432
Database: weather_db
Username: value of POSTGRES_USER from repos/.env
Password: value of POSTGRES_PASSWORD from repos/.env
```

SQLAlchemy URI:

```text
postgresql+psycopg2://<POSTGRES_USER>:<POSTGRES_PASSWORD>@database:5432/<POSTGRES_DB>
```

Then add datasets from:

```text
schema: weatherstack
tables: weather_data, bronze, gold
```

## Common Commands

Start everything:

```bash
docker compose up -d --build
```

Stop everything:

```bash
docker compose down
```

View logs:

```bash
docker compose logs -f airflow
docker compose logs -f database
docker compose logs -f superset
```

Remove orphan containers:

```bash
docker compose down --remove-orphans
```

Run dbt and remove one-off containers:

```bash
docker compose run --rm --remove-orphans dbt run
```

## Production Readiness Notes

This repository is a strong local production-style prototype, but Docker Compose is not a full production deployment strategy.

For production, the same architecture would usually be deployed with:

```text
Kubernetes or ECS
Managed Postgres or cloud warehouse
Secret manager
CI/CD pipeline
Centralized logs and metrics
Alerting
Backups
TLS/HTTPS
Role-based access control
```

## What Would Change In Production

### Deployment

Local:

```text
Docker Compose
```

Production:

```text
Kubernetes manifests or Helm charts
Separate deployments for Airflow webserver, scheduler, workers, Superset, Redis
Ingress controller and HTTPS
```

### Secrets

Local:

```text
.env files and Compose environment variables
```

Production:

```text
Kubernetes Secrets
AWS Secrets Manager
GCP Secret Manager
HashiCorp Vault
```

### Database

Local:

```text
Postgres container
```

Production:

```text
Managed Postgres for metadata
Snowflake, BigQuery, Redshift, Databricks, or managed Postgres for analytics
Automated backups
Read replicas if needed
```

### Airflow

Local:

```text
airflow standalone
```

Production:

```text
Airflow webserver
Airflow scheduler
Airflow workers
Airflow triggerer
Remote logs
Retry policies
Alerts
```

### Superset

Local:

```text
Single Superset web container
Postgres metadata DB
Redis cache
```

Production:

```text
Multiple Superset web workers
Celery workers
Celery beat
Redis
Postgres metadata DB
SSO/OAuth
HTTPS
Backups
```

### dbt

Local:

```text
Manual dbt container runs or Airflow DockerOperator
```

Production:

```text
Airflow KubernetesPodOperator
dbt Cloud
CI checks for dbt compile/test
dbt docs generated and published
```

## Future Development

Planned improvements:

```text
Add dbt tests for not_null, unique, accepted_values, and relationships
Add dbt freshness checks for source weather data
Add silver and gold models for analytics-ready reporting
Add incremental dbt models for larger datasets
Add Airflow retries and failure alerts
Add Slack/email notifications
Add CI/CD for linting, tests, Docker builds, and deployment
Move credentials to a secret manager
Add Kubernetes manifests or Helm charts
Add Superset dashboards as importable assets
Add monitoring with Prometheus and Grafana
Add data quality checks with Great Expectations or Soda
Add API extraction for multiple cities
Add historical weather ingestion
Add partitioning/indexing strategy in Postgres
```

## Current Status

The project currently supports:

```text
Python ETL into Postgres
Postgres storage
dbt transformations
Airflow orchestration
Superset visualization service
Containerized local runtime
```

This is a good foundation for a production data engineering portfolio project.
