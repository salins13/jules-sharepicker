import pandas as pd
import sqlite3
import os
import sys
import numpy as np

# Add the parent directory to the path to import the indicators module
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from technical_analysis.indicators import add_technical_indicators

DATABASE_NAME = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data', 'market_data.db'))

def run_backtest(stock_table, initial_capital=100000, stop_loss_pct=2, target_pct=5):
    """
    Runs a simplified backtest on a given stock's historical data.
    """
    conn = sqlite3.connect(DATABASE_NAME)
    df = pd.read_sql_query(f"SELECT * FROM {stock_table}", conn)
    conn.close()

    # Data preparation
    df = df.rename(columns={'Price': 'Datetime'})
    df = df.drop(df.index[0])
    df['Datetime'] = pd.to_datetime(df['Datetime'], errors='coerce')
    df.dropna(subset=['Datetime'], inplace=True)
    df.set_index('Datetime', inplace=True)
    df.sort_index(inplace=True)
    for col in ['Open', 'High', 'Low', 'Close', 'Volume']:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    df.dropna(inplace=True)

    # Add indicators
    df = add_technical_indicators(df)
    df.dropna(inplace=True)

    # Backtesting logic
    capital = initial_capital
    position = None
    trades = []

    for i in range(1, len(df)):
        current_row = df.iloc[i]

        # Entry condition (relaxed for demonstration)
        if position is None:
            supertrend_dir_col = [col for col in df.columns if 'SUPERTd' in col][0]
            if (current_row['Close'] > current_row['EMA_50'] and
                current_row['RSI_14'] > 55 and
                current_row['MACDh_12_26_9'] > 0 and
                current_row[supertrend_dir_col] == 1):

                entry_price = current_row['Close']
                position = {
                    "entry_price": entry_price,
                    "stop_loss": entry_price * (1 - stop_loss_pct / 100),
                    "target": entry_price * (1 + target_pct / 100)
                }

        # Exit condition
        elif position is not None:
            if current_row['Low'] <= position['stop_loss'] or current_row['High'] >= position['target']:
                exit_price = position['stop_loss'] if current_row['Low'] <= position['stop_loss'] else position['target']
                pnl = exit_price - position['entry_price']
                capital += pnl * (capital / position['entry_price']) # Simple position sizing
                trades.append(pnl)
                position = None

    # Performance metrics
    if not trades:
        return {"message": "No trades were executed."}

    win_rate = (len([t for t in trades if t > 0]) / len(trades)) * 100
    total_pnl = sum(trades)
    sharpe_ratio = np.mean(trades) / np.std(trades) if np.std(trades) != 0 else 0

    return {
        "stock": stock_table,
        "total_trades": len(trades),
        "win_rate_pct": win_rate,
        "total_pnl": total_pnl,
        "final_capital": capital,
        "sharpe_ratio": sharpe_ratio
    }


if __name__ == '__main__':
    # Example usage: backtest a few stocks
    stocks_to_test = ['RELIANCE_NS_1d', 'TCS_NS_1d', 'INFY_NS_1d']
    for stock in stocks_to_test:
        backtest_results = run_backtest(stock)
        print(f"--- Backtest Results for {stock} ---")
        print(backtest_results)
        print("\\n")
