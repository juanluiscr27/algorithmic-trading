# This is a Python script for an Equal-Weight S&P 500 Index Fund
import screener as sp500


def main():
    print("S&P 500 Index Fund Screener")
    sp500.import_stocks()
    sp500.search_symbol("AAPL")


if __name__ == '__main__':
    main()

