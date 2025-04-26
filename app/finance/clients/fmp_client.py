import requests
import os

from dotenv import load_dotenv

load_dotenv()

FMP_API_KEY = os.getenv("FMP_API_KEY")
FMP_BASE_URL = "https://financialmodelingprep.com/api/v3"
FMP_BASE_DEV_URL = "https://financialmodelingprep.com/stable/"
def fmp_get(endpoint, params=None):
    if params is None:
        params = {}
    params["apikey"] = FMP_API_KEY

    url = f"{FMP_BASE_URL}/{endpoint}"
    response = requests.get(url, params=params)

    if response.status_code != 200:
        raise Exception(f"FMP API error: {response.status_code} - {response.text}")

    return response.json()

def fmp_get_dev_env(endpoint):
    params = {}
    params["apikey"] = FMP_API_KEY

    url = f"{FMP_BASE_DEV_URL}/{endpoint}"
    response = requests.get(url, params=params)

    if response.status_code != 200:
        raise Exception(f"FMP API error: {response.status_code} - {response.text}")

    return response.json()