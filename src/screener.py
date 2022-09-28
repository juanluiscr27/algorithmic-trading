import numpy as np
import pandas as pd
import requests
import xlsxwriter
import math
from src.secrets import IEX_CLOUD_API_TOKEN


def import_stocks():
    stocks = pd.read_csv('./data/sp_500_stocks.csv')
    print(stocks)


def search_symbol(symbol=None):
    if not symbol:
        symbol = "AAPL"

    api_url = f"https://sandbox.iexapis.com/stock/{symbol}/quote/"
