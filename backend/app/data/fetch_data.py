import yfinance as yf
import pandas as pd
import os

# Define the list of tickers (example: Nifty 50)
TICKERS = [
    "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "ICICIBANK.NS",
    "HINDUNILVR.NS", "BHARTIARTL.NS", "ITC.NS", "KOTAKBANK.NS", "LT.NS"
]

# Define the intervals
INTERVALS = ["1m", "5m", "15m", "30m", "1d"]

# Define the data directory
DATA_DIR = "data"

def fetch_and_save_data():
    """
    Fetches historical data for the specified tickers and intervals,
    and saves it to CSV files.
    """
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)

    for ticker in TICKERS:
        for interval in INTERVALS:
            print(f"Fetching {interval} data for {ticker}...")
            try:
                # Fetch data
                # For intraday data, yfinance limits the period to the last 7 days for 1m, and 60 days for other intervals
                period = "7d" if interval == "1m" else "60d"
                data = yf.download(ticker, period=period, interval=interval)

                if not data.empty:
                    # Save to CSV
                    filename = f"{DATA_DIR}/{ticker}_{interval}.csv"
                    data.to_csv(filename)
                    print(f"Saved data to {filename}")
                else:
                    print(f"No data found for {ticker} at {interval} interval.")
            except Exception as e:
                print(f"Error fetching data for {ticker} ({interval}): {e}")

if __name__ == "__main__":
    fetch_and_save_data()
