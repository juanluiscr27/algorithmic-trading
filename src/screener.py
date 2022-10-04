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


def get_data(symbol):
    data = search_symbol(symbol)
    print("Stock: " + symbol)
    print(f"Latest Price: {data['latestPrice']}")
    print(f"Market Cap: {round(data['marketCap'] / 1e9, 2)}B")


def append_data(symbol):
    data = search_symbol(symbol)
    data_columns = ["Ticker", "Stock Price", "Market Capitalization", "Number of Shares to Buy"]
    df = pd.DataFrame(columns=data_columns)
    df = pd.concat([
        df,
        pd.Series([
            symbol,
            data["latestPrice"],
            data["marketCap"]/1e9,
            "NaN"
        ],
            index=data_columns
        ).to_frame().T],
        ignore_index=True
    )
    print(df)


def get_data_all():
    data_columns = ["Ticker", "Stock Price", "Market Capitalization", "Number of Shares to Buy"]
    df = pd.DataFrame(columns=data_columns)
    stocks = pd.read_csv('./data/sp_500_stocks.csv')
    for stock in stocks["Ticker"][:5]:
        api_url = f"https://sandbox.iexapis.com/stable/stock/{stock}/quote/?token={IEX_CLOUD_API_TOKEN}"
        data = requests.get(api_url).json()
        df = pd.concat([
            df,
            pd.Series([
                stock,
                data["latestPrice"],
                data["marketCap"],
                "NaN"
            ],
                index=data_columns
            ).to_frame().transpose()],
            ignore_index=True
        )

    print(df)


def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


def get_data_batch():
    stocks = pd.read_csv('./data/sp_500_stocks.csv')
    symbol_groups = chunks(stocks["Ticker"], 100)
    symbol_strings = []
    for index, symbol_group in enumerate(symbol_groups):
        symbol_strings.append(",".join(symbol_group))

    data_columns = ["Ticker", "Stock Price", "Market Capitalization", "Number of Shares to Buy"]
    df = pd.DataFrame(columns=data_columns)
    for symbol_str in symbol_strings:
        batch_call_api_url = f"https://sandbox.iexapis.com/stable/stock/market/batch?symbols=" \
                             f"{symbol_str}&types=quote&token={IEX_CLOUD_API_TOKEN}"
        data = requests.get(batch_call_api_url).json()
        for symbol in symbol_str.split(","):
            df = pd.concat([
                df,
                pd.Series([
                    symbol,
                    data[symbol]["quote"]["latestPrice"],
                    data[symbol]["quote"]["marketCap"],
                    "NaN"
                ],
                    index=data_columns
                ).to_frame().transpose()
            ],
                ignore_index=True
            )

    return df


def set_portfolio():
    size = input("Enter the value of your portfolio: ")
    try:
        value = float(size)
        return value
    except ValueError:
        print("Your input was not a valid number")
        return set_portfolio()


def get_shares_to_buy():
    value = set_portfolio()
    df = get_data_batch()
    position_size = value/len(df.index)
    for i in range(len(df.index)):
        df.loc[i, "Number of Shares to Buy"] = math.floor(position_size/df.loc[i, "Stock Price"])

    print(df)
