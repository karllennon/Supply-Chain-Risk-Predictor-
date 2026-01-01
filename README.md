Project Title: AI-Driven Supply Chain Risk & Delay Predictor
A Full-Stack Data Science Solution utilizing Medallion Architecture, Transformers (FinBERT), and XGBoost to predict logistics disruptions.

Executive Summary
This project addresses the "Predictive Gap" in global supply chains by merging internal logistics records (180,000+ rows) with external unstructured data (11,000+ news headlines). By building a SQL-based Medallion Architecture, I transformed messy CSV data into a validated "Gold Layer," enabling an XGBoost model to predict shipping delays with a Mean Absolute Error (MAE) of <1 day.

The Architecture (Medallion Pattern)
To ensure data integrity and scalability, the pipeline is organized into three distinct tiers:

Bronze Layer (Raw): Immutable landing zone for raw DataCo CSVs and JSON news datasets.

Silver Layer (Cleaned): Implementation of a SQL Quality Firewall that identified and filtered out ~2% of corrupted records (e.g., negative shipping times).

Gold Layer (Model-Ready): A high-performance feature set created by performing a temporal join between logistics dates and aggregated daily news sentiment.

The NLP Engine (Alternative Data)
A primary innovation of this project is the inclusion of "Alternative Data" to capture external market risks:

Model: Utilized FinBERT (a specialized Financial Transformer) to perform sentiment analysis on global headlines from 2015–2018.

Impact: The engineered daily_risk_score feature ranked in the Top 25% of predictors, successfully capturing how geopolitical and economic news directly impacts regional shipping performance.

Model Performance & Insights
I compared multiple ensemble methods to find the optimal balance between stability and accuracy:

Random Forest: Provided a stable baseline (MAE: 0.98 days).

XGBoost: Selected for deployment due to high performance on high-cardinality categorical data (MAE: 0.99 days).

Key Discovery: While "Shipping Mode" remains the strongest predictor, News Sentiment provided a critical "Risk Multiplier," accurately flagging delays during periods of high market volatility.

Tech Stack
Data Engineering: Python, SQLite, Pandas.

Machine Learning: XGBoost, Scikit-Learn.

NLP: HuggingFace Transformers (FinBERT), PyTorch.

Deployment: Streamlit, Joblib.

How to Run Locally
Clone: git clone https://github.com/your-username/supply-chain-predictor.git

Environment: python3 -m venv venv && source venv/bin/activate

Install: pip install -r requirements.txt

Launch Dashboard: streamlit run scripts/app.py