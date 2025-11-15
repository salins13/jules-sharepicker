import sqlite3
import pandas as pd
import os

DATABASE_NAME = "market_data.db"
DATA_DIR = "data"

def create_database():
    """
    Creates the SQLite database and tables for storing market data.
    """
    conn = sqlite3.connect(DATABASE_NAME)
    c = conn.cursor()

    # Create a table for each ticker and interval combination
    for filename in os.listdir(DATA_DIR):
        if filename.endswith(".csv"):
            table_name = filename.replace(".csv", "").replace(".", "_")
            df = pd.read_csv(os.path.join(DATA_DIR, filename))
            df.to_sql(table_name, conn, if_exists="replace", index=False)
            print(f"Created table {table_name} and inserted data.")

    conn.close()

if __name__ == "__main__":
    create_database()
