import logging
import os
from contextlib import closing
from pathlib import Path
from typing import Any

import psycopg2
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR.parent / ".env")
load_dotenv(BASE_DIR / ".env", override=True)

try:
    from .api_requests import fetch_data, mock_fetch_data
except ImportError:
    from api_requests import fetch_data, mock_fetch_data

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s %(levelname)s %(name)s - %(message)s",
)
logger = logging.getLogger(__name__)

CREATE_TABLE_SQL = """
create schema if not exists weatherstack;

create table if not exists weatherstack.weather_data(
    id serial primary key,
    city text not null,
    temperature numeric(6, 2) not null,
    weather_description text,
    wind_speed numeric(6, 2),
    time timestamp without time zone not null,
    inserted_at timestamp without time zone default now(),
    utc_offset text
);

create index if not exists weather_data_city_time_idx
    on weatherstack.weather_data(city, time desc);
"""


def get_env(*names: str, default: str | None = None) -> str:
    for name in names:
        value = os.getenv(name)
        if value:
            return value
    if default is not None:
        return default
    raise RuntimeError(f"Missing required environment variable. Tried: {', '.join(names)}")


def use_mock_data() -> bool:
    return os.getenv("USE_MOCK_WEATHER", "false").strip().lower() in {"1", "true", "yes"}


def connect_database():
    logger.info("Connecting to Postgres")
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", os.getenv("POSTGRES_HOST_PORT", "5001")),
        dbname=get_env("DB_NAME", "POSTGRES_DB"),
        user=get_env("DB_USER", "POSTGRES_USER"),
        password=get_env("DB_PASSWORD", "POSTGRES_PASSWORD"),
        connect_timeout=int(os.getenv("DB_CONNECT_TIMEOUT_SECONDS", "10")),
    )


def create_table(conn) -> None:
    logger.info("Ensuring weatherstack.weather_data exists")
    with conn.cursor() as cur:
        cur.execute(CREATE_TABLE_SQL)
    conn.commit()


def normalize_weather_payload(data: dict[str, Any]) -> dict[str, Any]:
    try:
        descriptions = data["current"].get("weather_descriptions") or []
        return {
            "city": data["location"]["name"],
            "temperature": data["current"]["temperature"],
            "weather_description": descriptions[0] if descriptions else None,
            "wind_speed": data["current"].get("wind_speed"),
            "time": data["location"]["localtime"],
            "utc_offset": data["location"].get("utc_offset"),
        }
    except KeyError as exc:
        raise ValueError(f"Weather payload is missing required field: {exc}") from exc


def insert_data(conn, data: dict[str, Any]) -> int:
    weather_record = normalize_weather_payload(data)
    logger.info("Inserting weather observation for %s", weather_record["city"])

    with conn.cursor() as cur:
        cur.execute(
            """
            insert into weatherstack.weather_data(
                city,
                temperature,
                weather_description,
                wind_speed,
                time,
                utc_offset
            )
            values (
                %(city)s,
                %(temperature)s,
                %(weather_description)s,
                %(wind_speed)s,
                %(time)s,
                %(utc_offset)s
            )
            returning id;
            """,
            weather_record,
        )
        inserted_id = cur.fetchone()[0]

    conn.commit()
    logger.info("Inserted weather observation id=%s", inserted_id)
    return inserted_id


def main() -> None:
    data = mock_fetch_data() if use_mock_data() else fetch_data()

    with closing(connect_database()) as conn:
        create_table(conn)
        insert_data(conn, data)
        logger.info("Database connection closed")


if __name__ == "__main__":
    main()
