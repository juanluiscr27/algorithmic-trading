import pandas as pd
import numpy as np
import requests
import math
from scipy import stats
from statistics import mean
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
        "One-Month Return Percentile",
        "HQM Score"
    ]

    hqm_df = pd.DataFrame(columns=hqm_columns)

    # Getting S&P500 symbols list
    stocks = pd.read_csv('./data/sp_500_stocks.csv')
    symbol_groups = chunks(stocks["Ticker"], 100)
    symbol_strings = []
    for _, symbol_group in enumerate(symbol_groups):
        symbol_strings.append(",".join(symbol_group))

    # API batch request
    for symbol_string in symbol_strings[:1]:
        batch_api_call_url = f"https://sandbox.iexapis.com/stable/stock/market/batch?" \
                             f"symbols={symbol_string}&types=price,stats&token={IEX_CLOUD_API_TOKEN}"
        data = requests.get(batch_api_call_url).json()
        for symbol in symbol_string.split(","):
            hqm_df = pd.concat([
                hqm_df,
                pd.Series([
                    symbol,
                    data[symbol]["price"],
                    np.nan,
                    data[symbol]["stats"]["year1ChangePercent"],
                    np.nan,
                    data[symbol]["stats"]["month6ChangePercent"],
                    np.nan,
                    data[symbol]["stats"]["month3ChangePercent"],
                    np.nan,
                    data[symbol]["stats"]["month1ChangePercent"],
                    np.nan,
                    np.nan
                ],
                    index=hqm_columns
                ).to_frame().T
            ],
                ignore_index=True
            )

    # Calculating the time periods percentiles
    time_periods = ["One-Year", "Six-Month", "Three-Month", "One-Month"]
    for row in hqm_df.index:
        for time_period in time_periods:
            hqm_df.loc[row, f"{time_period} Return Percentile"] = stats.percentileofscore(
                hqm_df[f"{time_period} Price Return"],
                hqm_df.loc[row, f"{time_period} Price Return"]
            )

    # print(hqm_df)
    return hqm_df


def hqm_score():
    hqm_df = high_quality_momentum()
    time_periods = ["One-Year", "Six-Month", "Three-Month", "One-Month"]

    for row in hqm_df.index:
        momentum_percentiles = []
        for time_period in time_periods:
            momentum_percentiles.append(hqm_df.loc[row, f"{time_period} Return Percentile"])

        hqm_df.loc[row, "HQM Score"] = mean(momentum_percentiles)

    # print(hqm_df)
    return hqm_df


def top_50_hqm():
    hqm_df = hqm_score()
    hqm_df.sort_values("HQM Score", ascending=False, inplace=True)
    hqm_df = hqm_df[:50]
    hqm_df.reset_index(drop=True, inplace=True)
    # print(hqm_df)
    return hqm_df


def get_hqm_shares_to_buy():
    hqm_df = top_50_hqm()
    portfolio_size = set_portfolio()
    position_size = float(portfolio_size)/len(hqm_df.index)
    for index in hqm_df.index:
        hqm_df.loc[index, "Number of Shares to Buy"] = math.floor(position_size / hqm_df.loc[index, "Price"])

    print(hqm_df)
