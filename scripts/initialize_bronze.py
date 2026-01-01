import pandas as pd
import sqlite3
import os

# Define file paths
csv_file = 'data/raw/DataCoSupplyChainDataset.csv'
db_file = 'data/processed/supply_chain.db'

print("--- Starting Bronze Layer Ingestion ---")

# 1. Load the dataset
# We use ISO-8859-1 encoding because this specific dataset often has special characters
try:
    df = pd.read_csv(csv_file, encoding='ISO-8859-1')
    print(f"Successfully loaded {len(df)} rows from CSV.")
except FileNotFoundError:
    print(f"Error: {csv_file} not found in the current directory.")
    exit()

# 2. Clean column names for SQL compatibility
# Replaces spaces and dots with underscores and removes parentheses
df.columns = (df.columns
              .str.replace(' ', '_')
              .str.replace('(', '')
              .str.replace(')', '')
              .str.replace('.', '')
              .str.lower())

# 3. Establish SQL Connection and Load Data
conn = sqlite3.connect(db_file)
df.to_sql('bronze_logistics', conn, index=False, if_exists='replace')

# 4. Verification
query = "SELECT COUNT(*) FROM bronze_logistics"
count = pd.read_sql(query, conn).iloc[0, 0]

print(f"Verification: {count} rows successfully written to 'bronze_logistics' table.")
conn.close()
print("--- Bronze Layer Initialized ---")