import pandas as pd
import sqlite3
import json

# 1. Load the JSON news data
# The file is in JSONL format (one JSON object per line)
news_data = []
with open('data/raw/News_Category_Dataset_v3.json', 'r') as f:
    for line in f:
        news_data.append(json.loads(line))

df_news = pd.DataFrame(news_data)

# 2. Filter for relevant categories to reduce noise
relevant_categories = ['BUSINESS', 'WORLD NEWS', 'TECH']
df_news = df_news[df_news['category'].isin(relevant_categories)]

# 3. Standardize the date to match your logistics table
df_news['date'] = pd.to_datetime(df_news['date'])

# 4. Save to Bronze SQL
conn = sqlite3.connect('data/processed/supply_chain.db')
df_news.to_sql('bronze_news', conn, index=False, if_exists='replace')
conn.close()

print(f"Bronze News Layer initialized: {len(df_news)} relevant headlines loaded.")