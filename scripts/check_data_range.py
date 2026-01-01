import sqlite3
import pandas as pd

conn = sqlite3.connect('supply_chain.db')

# Find the start and end dates of our validated shipments
query = """
SELECT 
    MIN(order_date) as start_date, 
    MAX(order_date) as end_date 
FROM silver_logistics
"""

df_range = pd.read_sql(query, conn)
print(f"Your shipping data runs from: {df_range['start_date'].values[0]} to {df_range['end_date'].values[0]}")

conn.close()