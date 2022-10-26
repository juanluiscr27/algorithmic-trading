# This is a Python script for an Equal-Weight S&P 500 Index Fund
import screener as sp500


def main():
    print("S&P 500 Index Fund Screener")
    sp500.import_stocks()
    # sp500.search_symbol("AAPL")
    # sp500.get_data("AAPL")
    # sp500.append_data("AAPL")
    # sp500.get_data_all()
    # sp500.get_data_batch()
    #sp500.get_shares_to_buy()


if __name__ == '__main__':
    main()
