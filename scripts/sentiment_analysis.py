import sqlite3
import pandas as pd
from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline
import torch

# 1. Setup paths and Model
db_path = 'data/processed/supply_chain.db'
model_name = "ProsusAI/finbert"

print("--- Initializing NLP Engine (FinBERT) ---")
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSequenceClassification.from_pretrained(model_name)
nlp = pipeline("sentiment-analysis", model=model, tokenizer=tokenizer)

# 2. Connect to DB and fetch headlines
conn = sqlite3.connect(db_path)
df_news = pd.read_sql("SELECT rowid, headline FROM bronze_news", conn)

print(f"Processing {len(df_news)} headlines. This may take a few minutes...")

# 3. Perform Sentiment Analysis
def get_sentiment(text):
    # Truncate text to fit model limits
    result = nlp(text[:512])[0]
    # We want a 'Risk Score' where negative news = higher value
    if result['label'] == 'negative':
        return result['score']
    elif result['label'] == 'positive':
        return 1 - result['score']
    else:
        return 0.5 # Neutral

# Applying the model (using a small sample first is a good 'Stats' move)
df_news['sentiment_score'] = df_news['headline'].apply(get_sentiment)

# 4. Save to Silver Layer
df_news[['headline', 'sentiment_score']].to_sql('silver_news_sentiment', conn, if_exists='replace', index=False)

print("--- NLP Sentiment Analysis Complete ---")
conn.close()