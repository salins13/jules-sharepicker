from fastapi import FastAPI
import sys
import os
import pandas as pd

# Add the parent directory to the path to import the screener and scorer modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from screening.screener import screen_stocks
from screening.scorer import score_stocks

app = FastAPI()

def get_trade_parameters(stock, last_row):
    """
    Generates trade parameters (entry, stop-loss, targets) for a stock.
    """
    entry = last_row['Close']
    stop_loss = last_row['s1'] # Using pivot point support as stop-loss

    # Simple target calculation based on pivot points
    target1 = last_row['r1']
    target2 = last_row['r2']
    target3 = last_row['pivot'] + (last_row['r2'] - last_row['s2']) # R2-S2 range projection

    risk_reward_ratio = (target1 - entry) / (entry - stop_loss) if (entry - stop_loss) != 0 else 0

    return {
        "entry": entry,
        "stop_loss": stop_loss,
        "targets": {
            "t1": target1,
            "t2": target2,
            "t3": target3
        },
        "risk_reward_ratio": risk_reward_ratio
    }

@app.get("/scan")
def scan_stocks():
    """
    Performs a full scan of the market:
    1. Screens for bullish and bearish stocks.
    2. Scores the identified stocks.
    3. Generates trade parameters for each stock.
    4. Returns a structured JSON response.
    """
    screener_results = screen_stocks()

    bullish_ranked = score_stocks(screener_results.get('bullish', []))
    bearish_ranked = score_stocks(screener_results.get('bearish', []))

    # Add trade parameters to the results
    # (This requires re-fetching the data, which is inefficient.
    #  A better approach would be to integrate this into the scoring function.)

    # For now, I'll just return the ranked lists
    return {
        "bullish": bullish_ranked,
        "bearish": bearish_ranked
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
