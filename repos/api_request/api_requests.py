import requests
import os
import sys
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("API_KEY")
api_url = f"https://api.weatherstack.com/current?access_key={API_KEY}&query=New%20York"



def fetch_data(api_url):
    try:
        print("Fetched started from weather data")
        response=requests.get(api_url)
        print("API response received successfully")
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        
#fetch_data(api_url)


def mock_fetch_data():
    return {'request': {'type': 'City', 'query': 'New York, United States of America', 'language': 'en', 'unit': 'm'}, 'location': {'name': 'New York', 'country': 'United States of America', 'region': 'New York', 'lat': '40.714', 'lon': '-74.006', 'timezone_id': 'America/New_York', 'localtime': '2026-05-12 17:05', 'localtime_epoch': 1778605500, 'utc_offset': '-4.0'}, 'current': {'observation_time': '09:05 PM', 'temperature': 18, 'weather_code': 113, 'weather_icons': ['https://cdn.worldweatheronline.com/images/wsymbols01_png_64/wsymbol_0001_sunny.png'], 'weather_descriptions': ['Sunny'], 'astro': {'sunrise': '05:42 AM', 'sunset': '08:03 PM', 'moonrise': '03:08 AM', 'moonset': '03:23 PM', 'moon_phase': 'Waning Crescent', 'moon_illumination': 29}, 'air_quality': {'co': '201.85', 'no2': '40.75', 'o3': '54', 'so2': '5.15', 'pm2_5': '12.95', 'pm10': '13.05', 'us-epa-index': '1', 'gb-defra-index': '1'}, 'wind_speed': 14, 'wind_degree': 202, 'wind_dir': 'SSW', 'pressure': 1020, 'precip': 0, 'humidity': 22, 'cloudcover': 0, 'feelslike': 18, 'uv_index': 2, 'visibility': 16, 'is_day': 'yes'}}


