import requests
import os
import sys
from dotenv import load_dotenv

load_dotenv()
API_KEY=os.getenv("API_KEY")


api_url=f"https://api.weatherstack.com/current? access_key = {API_KEY}& query = New York"

def fetch_data(api_url):
    response=requests.get(api_url)
    print(response)
    
fetch_data(api_url)

