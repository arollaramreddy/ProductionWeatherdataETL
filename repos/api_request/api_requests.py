import requests
import os
import sys
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("API_KEY")
api_url = f"https://api.weatherstack.com/current?access_key={API_KEY}&query=New%20York"



def fetch_data(api_url):
    try:
        response=requests.get(api_url)
        print("API response received successfully")
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"An error occured: {e}")
    
fetch_data(api_url)

