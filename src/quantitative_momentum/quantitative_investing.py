# This is a Python script for a Quantitative Momentum Investing Strategy
import strategy as mtm


def main():
    # mtm.import_stocks()
    # mtm.stats_api_call("AAPL")
    mtm.get_change_pct("AAPL")


if __name__ == "__main__":
    main()
