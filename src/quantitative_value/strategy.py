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
    api_url = f"https://sandbox.iexapis.com/stable/stock/{symbol}/quote?token={IEX_CLOUD_API_TOKEN}"
    data = requests.get(api_url).json()
    # print(data)
    return data


def parsing_data(symbol):
    data = stats_api_call(symbol)
    price = data["latestPrice"]
    pe_ratio = data["peRatio"]

    print(f"Price {price}")
    print(f"PE Ratio {pe_ratio}")


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

    data_columns = ["Ticker", "Price", "Price-to-Earnings Ratio", "Number of Shares to Buy"]
    df = pd.DataFrame(columns=data_columns)
    for symbol_string in symbol_strings:
        batch_api_call_url = f"https://sandbox.iexapis.com/stable/stock/market/batch?" \
                             f"symbols={symbol_string}&types=quote&token={IEX_CLOUD_API_TOKEN}"
        data = requests.get(batch_api_call_url).json()
        for symbol in symbol_string.split(","):
            df = pd.concat([
                df,
                pd.Series([
                    symbol,
                    data[symbol]["quote"]["latestPrice"],
                    data[symbol]["quote"]["peRatio"],
                    "N/A"
                ],
                    index=data_columns
                ).to_frame().T
            ],
                ignore_index=True
            )

    # print(df)
    return df


def set_portfolio():
    size = input("Enter the value of your portfolio: ")
    try:
        value = float(size)
        return value
    except ValueError:
        print("Your input was not a valid number.")
        return set_portfolio()


def remove_glamour_stock():
    df = get_data_batch()
    df.sort_values("Price-to-Earnings Ratio", inplace=True)
    df = df[df["Price-to-Earnings Ratio"] > 0]
    df = df[:50]
    df.reset_index(inplace=True)
    df.drop("index", axis=1, inplace=True)
    # print(df)
    return df


def get_shares_to_buy():
    value_stocks = remove_glamour_stock()
    portfolio_size = set_portfolio()
    position_size = portfolio_size / len(value_stocks.index)

    for row in value_stocks.index:
        value_stocks.loc[row, "Number of Shares to Buy"] = math.floor(
            position_size / value_stocks.loc[row, "Price"]
        )

    print(value_stocks)


def high_quality_value():
    # Get stock symbols list
    stocks = pd.read_csv('./data/sp_500_stocks.csv')
    symbol_groups = chunks(stocks["Ticker"], 100)
    symbol_strings = []
    for _, symbol_group in enumerate(symbol_groups):
        symbol_strings.append(",".join(symbol_group))

    # Columns names
    hqv_columns = [
        "Ticker",
        "Price",
        "Price-To-Earnings Ratio",
        "PE Percentile",
        "Price-To-Book Ratio",
        "PB Percentile",
        "Price-To-Sales Ratio",
        "PS Percentile",
        "EV/EBITDA",
        "EV/EBITDA Percentile",
        "EV/Gross Profit",
        "EV/Gross Profit Percentile",
        "HQV Score",
        "Number of Shares to Buy"
    ]

    hqv_df = pd.DataFrame(hqv_columns)

    # API Batch call request
    for symbol_string in symbol_strings:
        batch_api_call_url = f"https://sandbox.iexapis.com/stable/stock/market/batch?" \
                             f"symbols={symbol_string}&types=quote,advanced-stats&token={IEX_CLOUD_API_TOKEN}"

        data = requests.get(batch_api_call_url).json()

        for symbol in symbol_string.split(","):
            enterprise_value = data[symbol]["advanced-stats"]["enterpriseValue"]
            ebitda = data[symbol]["advanced-stats"]["EBITDA"]
            gross_profit = data[symbol]["advanced-stats"]["grossProfit"]
            try:
                ev_to_ebitda = enterprise_value / ebitda
            except TypeError:
                ev_to_ebitda = np.nan

            try:
                ev_to_gross_profit = enterprise_value / gross_profit
            except TypeError:
                ev_to_gross_profit = np.nan

            hqv_df = pd.concat([
                hqv_df,
                pd.Series([
                    symbol,
                    data[symbol]["quote"]["latestPrice"],
                    data[symbol]["quote"]["peRatio"],
                    np.nan,
                    data[symbol]["advanced-stats"]["priceToBook"],
                    np.nan,
                    data[symbol]["advanced-stats"]["priceToSales"],
                    np.nan,
                    ev_to_ebitda,
                    np.nan,
                    ev_to_gross_profit,
                    np.nan,
                    np.nan,
                    np.nan
                ],
                    index=hqv_columns,
                ).to_frame().T
            ],
                ignore_index=True
            )

    # Dealing with missing data
    for column in ["Price-To-Earnings Ratio", "Price-To-Book Ratio", "Price-To-Sales Ratio", "EV/EBITDA", "EV/Gross Profit"]:
        hqv_df[column].fillna(hqv_df[column].mean(), inplace=True)

    # Calculating Percentiles
    metrics = {
        "Price-To-Earnings Ratio": "PE Percentile",
        "Price-To-Book Ratio": "PB Percentile",
        "Price-To-Sales Ratio": "PS Percentile",
        "EV/EBITDA": "EV/EBITDA Percentile",
        "EV/Gross Profit": "EV/Gross Profit Percentile"
    }

    for metric in metrics.keys():
        for row in hqv_df.index:
            hqv_df.loc[row, metrics[metric]] = stats.percentileofscore(hqv_df[metric], hqv_df.loc[row, metric])

    # print(hqv_df-)
    return hqv_df


def hqv_score():
    hqv_df = high_quality_value()
    metrics = {
        "Price-To-Earnings Ratio": "PE Percentile",
        "Price-To-Book Ratio": "PB Percentile",
        "Price-To-Sales Ratio": "PS Percentile",
        "EV/EBITDA": "EV/EBITDA Percentile",
        "EV/Gross Profit": "EV/Gross Profit Percentile"
    }
    for row in hqv_df.index:
        values_percentiles = []
        for metric in metrics.keys():
            values_percentiles.append(hqv_df.loc[row, metrics[metric]])

        hqv_df.loc[row, "HQV Score"] = mean(values_percentiles)

    print(hqv_df)
