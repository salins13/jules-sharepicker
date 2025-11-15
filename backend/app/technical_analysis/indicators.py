import pandas as pd
import pandas_ta as ta

def add_technical_indicators(df):
    """
    Calculates and adds a comprehensive set of technical indicators to the dataframe.
    """
    # Trend Indicators
    df.ta.ema(length=9, append=True)
    df.ta.ema(length=20, append=True)
    df.ta.ema(length=50, append=True)
    df.ta.ema(length=200, append=True)
    df.ta.sma(length=20, append=True)
    df.ta.sma(length=50, append=True)
    df.ta.supertrend(length=7, multiplier=3, append=True)
    df.ta.adx(length=14, append=True)

    # Momentum Indicators
    df.ta.rsi(length=14, append=True)
    df.ta.macd(fast=12, slow=26, signal=9, append=True)
    df.ta.stoch(k=14, d=3, smooth_k=3, append=True)

    # Volume-based Indicators
    df.ta.vwap(append=True)
    df.ta.obv(append=True)
    df.ta.mfi(length=14, append=True)
    # Volume spike % relative to 20-period average
    df['volume_spike'] = (df['Volume'] / df['Volume'].rolling(window=20).mean()) * 100

    # Volatility-based Indicators
    df.ta.atr(length=14, append=True)
    df.ta.bbands(length=20, std=2, append=True)

    # Price-Action Features (basic implementation)
    # Pivot Points (can be enhanced with CPR)
    df['pivot'] = (df['High'] + df['Low'] + df['Close']) / 3
    df['r1'] = 2 * df['pivot'] - df['Low']
    df['s1'] = 2 * df['pivot'] - df['High']
    df['r2'] = df['pivot'] + (df['High'] - df['Low'])
    df['s2'] = df['pivot'] - (df['High'] - df['Low'])

    return df

if __name__ == '__main__':
    # Example Usage:
    # Load some data
    data_path = '../data/data/RELIANCE.NS_1d.csv'
    df = pd.read_csv(data_path, parse_dates=['Price'])
    df.set_index('Price', inplace=True)
    df.sort_index(inplace=True)

    # Ensure OHLCV columns are numeric
    for col in ['Open', 'High', 'Low', 'Close', 'Volume']:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    # Drop rows with NaN values that might have been introduced
    df.dropna(inplace=True)

    # Calculate indicators
    df_with_indicators = add_technical_indicators(df)

    # Print the last 5 rows with the new indicators
    print(df_with_indicators.tail())
