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
    # print(data)
    return data


def get_change_pct(symbol):
    data = stats_api_call(symbol)
    print(data['year1ChangePercent'])


def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


def get_data_batch():
    stocks = pd.read_csv('./data/sp_500_stocks.csv')
    symbol_groups = chunks(stocks["Ticker"], 100)
    symbol_strings = []
    for _, symbol_group in enumerate(symbol_groups):
        symbol_strings.append(",".join(symbol_group))

    data_columns = ["Ticker", "Price", "One-Year Price Return", "Number of Shares to Buy"]
    df = pd.DataFrame(columns=data_columns)
    for symbol_string in symbol_strings:
        batch_api_call_url = f"https://sandbox.iexapis.com/stable/stock/market/batch?" \
                             f"symbols={symbol_string}&types=price,stats&token={IEX_CLOUD_API_TOKEN}"
        data = requests.get(batch_api_call_url).json()
        for symbol in symbol_string.split(","):
            df = pd.concat([
                df,
                pd.Series([
                    symbol,
                    data[symbol]["price"],
                    data[symbol]["stats"]["year1ChangePercent"],
                    "N/A"
                ],
                    index=data_columns
                ).to_frame().T
            ],
                ignore_index=True
            )

    # print(df)
    return df


def remove_low_momentum():
    df = get_data_batch()
    df.sort_values("One-Year Price Return", ascending=False, inplace=True)
    high_momentum_stocks = df[:50]
    high_momentum_stocks.reset_index(inplace=True)
    # print(high_momentum_stocks)
    return high_momentum_stocks


def set_portfolio():
    size = input("Enter the value of your portfolio: ")
    try:
        value = float(size)
        return value
    except ValueError:
        print("Your input was not a valid number.")
        return set_portfolio()


def get_shares_to_buy():
    high_momentum_stocks = remove_low_momentum()
    portfolio_size = set_portfolio()
    position_size = portfolio_size / len(high_momentum_stocks.index)
    for index in range(len(high_momentum_stocks)):
        high_momentum_stocks.loc[
            index,
            "Number of Shares to Buy"
        ] = math.floor(position_size / high_momentum_stocks.loc[index, "Price"])

    print(high_momentum_stocks)


def high_quality_momentum():
    # Defining Data Frame columns
    hqm_columns = [
        "Ticker",
        "Price",
        "Number of Shares to Buy",
        "One-Year Price Return",
        "One-Year Return Percentile",
        "Six-Month Price Return",
        "Six-Month Return Percentile",
        "Three-Month Price Return",
        "Three-Month Return Percentile",
        "One-Month Price Return",
        "One-Month Return Percentile"
    ]

    hdm_df = pd.DataFrame(columns=hqm_columns)

    # Getting S&P500 symbols list
    stocks = pd.read_csv('./data/sp_500_stocks.csv')
    symbol_groups = chunks(stocks["Ticker"], 100)
    symbol_strings = []
    for _, symbol_group in enumerate(symbol_groups):
        symbol_strings.append(",".join(symbol_group))

    # API batch request
    for symbol_string in symbol_strings:
        batch_api_call_url = f"https://sandbox.iexapis.com/stable/stock/market/batch?" \
                             f"symbols={symbol_string}&types=price,stats&token={IEX_CLOUD_API_TOKEN}"
        data = requests.get(batch_api_call_url).json()
        for symbol in symbol_string.split(","):
            hdm_df = pd.concat([
                hdm_df,
                pd.Series([
                    symbol,
                    data[symbol]["price"],
                    "N/A",
                    data[symbol]["stats"]["year1ChangePercent"],
                    "N/A",
                    data[symbol]["stats"]["month6ChangePercent"],
                    "N/A",
                    data[symbol]["stats"]["month3ChangePercent"],
                    "N/A",
                    data[symbol]["stats"]["month1ChangePercent"],
                    "N/A"
                ],
                    index=hqm_columns
                ).to_frame().T
            ],
                ignore_index=True
            )

    # Calculating the time periods percentiles
    time_periods = ["One-Year", "Six-Month" "Three-Month", "One-Month"]

    for row in hdm_df.index:
        for time_period in time_periods:
            hdm_df.loc[row, f"{time_period} Return Percentile"] = 0

    print(hdm_df)
