DO $$
BEGIN
  IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'ram_airflow') THEN
    CREATE USER ram_airflow WITH PASSWORD 'airflow_password';
  END IF;

  IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'superset') THEN
    CREATE USER superset WITH PASSWORD 'superset_password';
  END IF;
END
$$;

SELECT 'CREATE DATABASE airflow_db OWNER ram_airflow'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'airflow_db')\gexec

SELECT 'CREATE DATABASE superset_db OWNER superset'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'superset_db')\gexec
