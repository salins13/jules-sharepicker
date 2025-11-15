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

def calculate_score(row):
    """
    Calculates a score (0-100) for a stock based on a weighted average of its technical indicators.
    """
    score = 0
    weights = {
        'trend': 0.3,
        'momentum': 0.3,
        'volume': 0.2,
        'volatility': 0.2
    }

    # Trend score (max 30)
    trend_score = 0
    if row['Close'] > row['EMA_200']: trend_score += 5
    if row['Close'] > row['EMA_50']: trend_score += 5
    if row['Close'] > row['EMA_20']: trend_score += 5
    if row['ADX_14'] > 25: trend_score += 5
    if [col for col in row.index if 'SUPERTd' in col][0] == 1: trend_score += 10
    score += trend_score * weights['trend']

    # Momentum score (max 30)
    momentum_score = 0
    if row['RSI_14'] > 60: momentum_score += 10
    elif row['RSI_14'] > 50: momentum_score += 5
    if row['MACDh_12_26_9'] > 0: momentum_score += 10
    if row['STOCHk_14_3_3'] > row['STOCHd_14_3_3'] and row['STOCHk_14_3_3'] < 80: momentum_score += 10
    score += momentum_score * weights['momentum']

    # Volume score (max 20)
    volume_score = 0
    if row['volume_spike'] > 200: volume_score += 10
    elif row['volume_spike'] > 150: volume_score += 5
    if row['MFI_14'] > 50: volume_score += 10
    score += volume_score * weights['volume']

    # Volatility score (max 20)
    volatility_score = 0
    bbu_col = [col for col in row.index if 'BBU' in col][0]
    bbl_col = [col for col in row.index if 'BBL' in col][0]
    bbm_col = [col for col in row.index if 'BBM' in col][0]

    # Lower bollinger band squeeze indicates potential for volatility
    if (row[bbu_col] - row[bbl_col]) / row[bbm_col] < 0.1:
        volatility_score += 10
    score += volatility_score * weights['volatility']

    return min(100, score)


def score_stocks(stocks):
    """
    Scores a list of stocks and returns a ranked list of dictionaries.
    """
    conn = sqlite3.connect(DATABASE_NAME)
    scored_stocks = []

    for stock in stocks:
        try:
            df = pd.read_sql_query(f"SELECT * FROM {stock}", conn)

            df = df.rename(columns={'Price': 'Datetime'})
            df = df.drop(df.index[0])
            df['Datetime'] = pd.to_datetime(df['Datetime'], errors='coerce')
            df.dropna(subset=['Datetime'], inplace=True)
            df.set_index('Datetime', inplace=True)
            df.sort_index(inplace=True)

            for col in ['Open', 'High', 'Low', 'Close', 'Volume']:
                 df[col] = pd.to_numeric(df[col], errors='coerce')

            df.dropna(inplace=True)

            df = add_technical_indicators(df)
            last_row = df.iloc[-1]
            score = calculate_score(last_row)

            scored_stocks.append({
                "stock": stock,
                "score": score
            })

        except Exception as e:
            print(f"Error scoring stock {stock}: {e}")
            continue

    conn.close()

    # Sort stocks by score in descending order
    return sorted(scored_stocks, key=lambda x: x['score'], reverse=True)


if __name__ == '__main__':
    from screener import screen_stocks

    results = screen_stocks()
    bullish_stocks = results['bullish']

    ranked_stocks = score_stocks(bullish_stocks)
    print("Ranked Bullish Stocks:")
    print(ranked_stocks)
