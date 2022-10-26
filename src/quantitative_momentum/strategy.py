import pandas as pd
# import numpy as np
# import requests
# import math
# from scipy import stats


def import_stocks():
    stocks = pd.read_csv('./data/sp_500_stocks.csv')
    print(stocks)
