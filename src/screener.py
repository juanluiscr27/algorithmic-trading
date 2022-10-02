import numpy as np
import pandas as pd
import requests
import xlsxwriter
import math
from src.project_secrets import IEX_CLOUD_API_TOKEN


def import_stocks():
    stocks = pd.read_csv('./data/sp_500_stocks.csv')
    print(stocks)


def search_symbol(symbol):
    api_url = f"https://sandbox.iexapis.com/stable/stock/{symbol}/quote/?token={IEX_CLOUD_API_TOKEN}"
    data = requests.get(api_url)
    print(f"SEARCH STATUS CODE: {data.status_code}")
    return data.json()


def get_info(symbol):
    data = search_symbol(symbol)
    print("Stock: " + symbol)
    print(f"Latest Price: {data['latestPrice']}")
    print(f"Market Cap: {round(data['marketCap']/1e9,2)}B")

