# This is a Python script for a Quantitative Momentum Investing Strategy
import strategy as mtm


def main():
    # mtm.import_stocks()
    # mtm.stats_api_call("AAPL")
    # mtm.get_change_pct("AAPL")
    # mtm.get_data_batch()
    # mtm.remove_low_momentum()
    # mtm.get_shares_to_buy()
    # mtm.high_quality_momentum()
    # mtm.hqm_score()
    # mtm.top_50_hqm()
    mtm.get_hqm_shares_to_buy()


if __name__ == "__main__":
    main()
