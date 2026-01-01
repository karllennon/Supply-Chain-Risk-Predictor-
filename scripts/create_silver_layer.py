import sqlite3
import pandas as pd

conn = sqlite3.connect('data/processed/supply_chain.db')
cursor = conn.cursor()

print("--- Starting Silver Layer Transformation (Quality Firewall) ---")

# 1. Define the SQL Transformation
silver_sql = """
CREATE TABLE IF NOT EXISTS silver_logistics AS
SELECT 
    order_id,
    category_name,
    customer_segment,
    order_region,
    shipping_mode,
    order_status,
    -- 1. Create the 'North Star' Metric
    days_for_shipping_real as actual_days,
    days_for_shipment_scheduled as scheduled_days,
    (days_for_shipping_real - days_for_shipment_scheduled) as delay_days,
    -- 2. Clean Timestamps
    order_date_dateorders as order_date,
    shipping_date_dateorders as shipping_date
FROM bronze_logistics
WHERE 
    -- 3. THE QUALITY FIREWALL
    days_for_shipping_real >= 0 -- Removes data errors with negative shipping times
    AND order_status != 'CANCELED' -- Focus on orders that were actually shipped
    AND actual_days IS NOT NULL; -- Ensure we have our target variable
"""

# 2. Execute and Verify
try:
    # Drop existing table if you're re-running
    cursor.execute("DROP TABLE IF EXISTS silver_logistics")
    cursor.execute(silver_sql)
    conn.commit()
    
    # Check how many rows passed the firewall
    count = pd.read_sql("SELECT COUNT(*) FROM silver_logistics", conn).iloc[0,0]
    removed = 180519 - count
    print(f"Silver Layer Created: {count} rows validated.")
    print(f"Quality Firewall Result: {removed} rows filtered out as noise/errors.")

except Exception as e:
    print(f"Error: {e}")

conn.close()