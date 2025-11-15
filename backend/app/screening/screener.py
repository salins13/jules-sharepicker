import pandas as pd
import sqlite3
import os
import sys

# Add the parent directory to the path to import the indicators module
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from technical_analysis.indicators import add_technical_indicators

# Construct an absolute path to the database
DATABASE_NAME = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data', 'market_data.db'))

def get_all_tables(conn):
    """Gets all table names from the SQLite database."""
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    return [table[0] for table in cursor.fetchall()]

def screen_stocks():
    """
    Screens stocks based on predefined bullish and bearish conditions.
    """
    conn = sqlite3.connect(DATABASE_NAME)
    tables = get_all_tables(conn)

    bullish_stocks = []
    bearish_stocks = []

    for table in tables:
        try:
            df = pd.read_sql_query(f"SELECT * FROM {table}", conn)

            # The date column is named 'Price', and the second row is garbage
            df = df.rename(columns={'Price': 'Datetime'})
            df = df.drop(df.index[0])
            df['Datetime'] = pd.to_datetime(df['Datetime'], errors='coerce')
            df.dropna(subset=['Datetime'], inplace=True)
            df.set_index('Datetime', inplace=True)
            df.sort_index(inplace=True)

            # Ensure columns are numeric
            for col in ['Open', 'High', 'Low', 'Close', 'Volume']:
                 df[col] = pd.to_numeric(df[col], errors='coerce')

            df.dropna(inplace=True)

            # Add technical indicators
            df = add_technical_indicators(df)

            # Get the last row for the most recent data
            last_row = df.iloc[-1]

            # Find the Supertrend direction column
            supertrend_dir_col = [col for col in df.columns if 'SUPERTd' in col][0]

            # Bullish conditions
            if (last_row['Close'] > last_row['VWAP_D'] and
                last_row['Close'] > last_row['EMA_20'] and
                last_row['volume_spike'] > 150 and
                50 < last_row['RSI_14'] < 65 and
                last_row['MACDh_12_26_9'] > 0 and
                last_row[supertrend_dir_col] == 1 and # Supertrend direction is up
                last_row['ADX_14'] > 20):
                bullish_stocks.append(table)

            # Bearish conditions
            if (last_row['Close'] < last_row['VWAP_D'] and
                last_row['Close'] < last_row['EMA_20'] and
                last_row['volume_spike'] > 150 and
                30 < last_row['RSI_14'] < 40 and
                last_row['MACDh_12_26_9'] < 0 and
                last_row[supertrend_dir_col] == -1 and # Supertrend direction is down
                last_row['ADX_14'] > 20):
                bearish_stocks.append(table)
        except Exception as e:
            print(f"Error processing table {table}: {e}")
            continue

    conn.close()
    return {"bullish": bullish_stocks, "bearish": bearish_stocks}

if __name__ == "__main__":
    results = screen_stocks()
    print("Bullish Stocks:")
    print(results['bullish'])
    print("\nBearish Stocks:")
    print(results['bearish'])
