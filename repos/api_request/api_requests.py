import os
from pathlib import Path

import requests
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR.parent / ".env")
load_dotenv(BASE_DIR / ".env", override=True)

DEFAULT_WEATHERSTACK_URL = "https://api.weatherstack.com/current"
api_url = os.getenv("WEATHERSTACK_BASE_URL", DEFAULT_WEATHERSTACK_URL)


def _required_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


def fetch_data(endpoint: str | None = None) -> dict:
    """Fetch current weather data from Weatherstack."""
    weather_city = os.getenv("WEATHER_CITY", "New York")
    timeout_seconds = int(os.getenv("WEATHERSTACK_TIMEOUT_SECONDS", "20"))

    response = requests.get(
        endpoint or api_url,
        params={
            "access_key": _required_env("API_KEY"),
            "query": weather_city,
        },
        timeout=timeout_seconds,
    )
    response.raise_for_status()

    payload = response.json()
    if payload.get("success") is False:
        error = payload.get("error", {})
        code = error.get("code", "unknown")
        info = error.get("info", "Weatherstack returned an error")
        raise RuntimeError(f"Weatherstack API error {code}: {info}")

    return payload


def mock_fetch_data() -> dict:
    return {
        "request": {
            "type": "City",
            "query": "New York, United States of America",
            "language": "en",
            "unit": "m",
        },
        "location": {
            "name": "New York",
            "country": "United States of America",
            "region": "New York",
            "lat": "40.714",
            "lon": "-74.006",
            "timezone_id": "America/New_York",
            "localtime": "2026-05-12 17:05",
            "localtime_epoch": 1778605500,
            "utc_offset": "-4.0",
        },
        "current": {
            "observation_time": "09:05 PM",
            "temperature": 18,
            "weather_code": 113,
            "weather_icons": [
                "https://cdn.worldweatheronline.com/images/wsymbols01_png_64/wsymbol_0001_sunny.png"
            ],
            "weather_descriptions": ["Sunny"],
            "astro": {
                "sunrise": "05:42 AM",
                "sunset": "08:03 PM",
                "moonrise": "03:08 AM",
                "moonset": "03:23 PM",
                "moon_phase": "Waning Crescent",
                "moon_illumination": 29,
            },
            "air_quality": {
                "co": "201.85",
                "no2": "40.75",
                "o3": "54",
                "so2": "5.15",
                "pm2_5": "12.95",
                "pm10": "13.05",
                "us-epa-index": "1",
                "gb-defra-index": "1",
            },
            "wind_speed": 14,
            "wind_degree": 202,
            "wind_dir": "SSW",
            "pressure": 1020,
            "precip": 0,
            "humidity": 22,
            "cloudcover": 0,
            "feelslike": 18,
            "uv_index": 2,
            "visibility": 16,
            "is_day": "yes",
        },
    }
