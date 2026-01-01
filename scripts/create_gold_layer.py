import sqlite3
import pandas as pd

db_path = 'data/processed/supply_chain.db'
conn = sqlite3.connect(db_path)

print("--- Creating Gold Layer (Model-Ready Dataset) ---")

# This SQL query does three things:
# 1. Aggregates news sentiment by date (Daily Average)
# 2. Cleans the messy logistics dates to match the news dates
# 3. Joins them into a final feature set
gold_sql = """
WITH daily_sentiment AS (
    -- Group news by date to get a single 'Risk Score' per day
    SELECT 
        DATE(n.date) as news_date,
        AVG(s.sentiment_score) as daily_risk_score
    FROM bronze_news n
    JOIN silver_news_sentiment s ON n.headline = s.headline
    GROUP BY 1
)
SELECT 
    l.*,
    COALESCE(d.daily_risk_score, 0.5) as daily_risk_score -- Use 0.5 (Neutral) if no news exists for that day
FROM silver_logistics l
LEFT JOIN daily_sentiment d ON 
    -- We parse the logistics date (MM/DD/YYYY) to match SQL's YYYY-MM-DD
    DATE(
        substr(l.order_date, 7, 4) || '-' || 
        printf('%02d', substr(l.order_date, 1, instr(l.order_date, '/') - 1)) || '-' || 
        printf('%02d', substr(substr(l.order_date, instr(l.order_date, '/') + 1), 1, instr(substr(l.order_date, instr(l.order_date, '/') + 1), '/') - 1))
    ) = d.news_date;
"""

try:
    # 2. Execute and Save
    df_gold = pd.read_sql(gold_sql, conn)
    
    # Save to the Gold Table
    df_gold.to_sql('gold_supply_chain', conn, if_exists='replace', index=False)
    
    print(f"Gold Layer Created! {len(df_gold)} rows prepared for Machine Learning.")
    print("Columns available:", df_gold.columns.tolist())

except Exception as e:
    print(f"SQL Error: {e}")

conn.close()