import sqlite3
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from xgboost import XGBRegressor
from sklearn.metrics import mean_absolute_error, r2_score
import joblib

# 1. Load Data
db_path = 'data/processed/supply_chain.db'
conn = sqlite3.connect(db_path)
df = pd.read_sql("SELECT * FROM gold_supply_chain", conn)
conn.close()

print(f"--- Starting Model Training on {len(df)} rows ---")

# 2. Feature Selection & Encoding
features = ['category_name', 'customer_segment', 'order_region', 'shipping_mode', 'scheduled_days', 'daily_risk_score']
target = 'delay_days'

X = df[features]
y = df[target]

X = pd.get_dummies(X, drop_first=True)

# 3. Train/Test Split (80/20)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 4. Model 1: Random Forest (The Baseline)
print("Training Random Forest...")
rf_model = RandomForestRegressor(n_estimators=100, max_depth=10, random_state=42)
rf_model.fit(X_train, y_train)

# 5. Model 2: XGBoost (The Performance Leader)
print("Training XGBoost...")
xgb_model = XGBRegressor(n_estimators=100, learning_rate=0.1, max_depth=6, random_state=42)
xgb_model.fit(X_train, y_train)

# 6. Evaluation
def evaluate(model, name):
    preds = model.predict(X_test)
    mae = mean_absolute_error(y_test, preds)
    r2 = r2_score(y_test, preds)
    print(f"\n[{name} Results]")
    print(f"Mean Absolute Error: {mae:.2f} days")
    print(f"R-Squared: {r2:.4f}")
    return preds

rf_preds = evaluate(rf_model, "Random Forest")
xgb_preds = evaluate(xgb_model, "XGBoost")

# 7. Visualizing Feature Importance (The "Insight" Step)
print("\nGenerating Feature Importance Plot...")
importances = xgb_model.feature_importances_
feat_importances = pd.Series(importances, index=X.columns)
feat_importances.nlargest(10).plot(kind='barh', color='teal')
plt.title("Top 10 Factors Predicting Shipping Delays")
plt.xlabel("Importance Score")
plt.tight_layout()
plt.savefig('notebooks/feature_importance.png')

# 8. Exporting for Deployment
joblib.dump(xgb_model, 'data/processed/supply_chain_model.pkl')
joblib.dump(X.columns.tolist(), 'data/processed/model_features.pkl')

print("--- Phase 4: Modeling Complete ---")