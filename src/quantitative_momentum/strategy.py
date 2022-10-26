import pandas as pd
import numpy as np
import requests
import math
from scipy import stats
from src.sp500.project_secrets import IEX_CLOUD_API_TOKEN


def import_stocks():
    stocks = pd.read_csv('./data/sp_500_stocks.csv')
    print(stocks)


def stats_api_call(symbol):
    api_url = f"https://sandbox.iexapis.com/stable/stock/{symbol}/stats?token={IEX_CLOUD_API_TOKEN}"
    data = requests.get(api_url).json()
    print(data)
