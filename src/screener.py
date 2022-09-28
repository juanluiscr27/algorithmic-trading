import numpy as np
import pandas as pd
import requests
import xlsxwriter
import math


def import_stocks():
    stocks = pd.read_csv('./data/sp_500_stocks.csv')
    print(stocks)
