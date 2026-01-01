import streamlit as st
import pandas as pd
import joblib
import sqlite3
import numpy as np

st.set_page_config(page_title="Supply Chain Risk Predictor", layout="wide")

@st.cache_resource
def load_resources():
    db_path = 'data/processed/supply_chain.db'
    conn = sqlite3.connect(db_path)
    
    # Load regions
    regions = pd.read_sql("SELECT DISTINCT order_region FROM gold_supply_chain", conn)['order_region'].tolist()
    
    # Get top 10 categories to keep the UI clean
    cat_counts = pd.read_sql("SELECT category_name, COUNT(*) as c FROM gold_supply_chain GROUP BY 1 ORDER BY c DESC", conn)
    top_categories = cat_counts['category_name'].head(10).tolist()
    categories_list = sorted(top_categories + ["Other"])
    
    total_rows = pd.read_sql("SELECT COUNT(*) FROM gold_supply_chain", conn).iloc[0,0]
    
    # Load the trained model artifacts
    model = joblib.load('data/processed/supply_chain_model.pkl')
    model_features = joblib.load('data/processed/model_features.pkl')
    
    conn.close()
    return regions, categories_list, total_rows, model, model_features

# Unpack the returned resources
regions, categories, total_rows, model, model_features = load_resources()

st.title("🚚 AI Supply Chain Delay Predictor")
st.markdown("Predict shipping delays using Logistics Data + Real-time News Sentiment.")

# Sidebar - Inputs
st.sidebar.header("Shipment Details")
mode = st.sidebar.selectbox("Shipping Mode", ["Standard Class", "Second Class", "First Class", "Same Day"])
region = st.sidebar.selectbox("Region", sorted(regions))
category = st.sidebar.selectbox("Category", categories)
days_scheduled = st.sidebar.slider("Scheduled Days", 0, 6, 3)

st.sidebar.header("External Risk (NLP)")
risk_input = st.sidebar.slider("News Sentiment Risk Score", 0.0, 1.0, 0.5, 
                               help="0.0 = Very Positive News, 1.0 = High Global Risk/Strike")

if st.button("Predict Delay"):
    # Prepare input for model
    input_data = pd.DataFrame(np.zeros((1, len(model_features))), columns=model_features)
    
    # Fill in numericals
    input_data['scheduled_days'] = days_scheduled
    input_data['daily_risk_score'] = risk_input
    
    # Fill in categorical dummies
    if f'shipping_mode_{mode}' in model_features:
        input_data[f'shipping_mode_{mode}'] = 1
    if f'order_region_{region}' in model_features:
        input_data[f'order_region_{region}'] = 1
    
    # Only set category dummy if it's not "Other" and exists in features
    if category != "Other" and f'category_name_{category}' in model_features:
        input_data[f'category_name_{category}'] = 1

    # Prediction
    prediction = model.predict(input_data)[0]
    
    # Calculate display delta (News impact relative to neutral 0.5)
    # This helps visualize how much the slider is moving the needle
    risk_impact = (risk_input - 0.5) * 1.5 
    
    st.metric("Predicted Delay", f"{prediction:.2f} Days", delta=f"{risk_impact:.2f} due to News")
    
    if prediction > 1.0:
        st.warning("⚠️ High Risk of Delay Detected")
    else:
        st.success("✅ On-track for on-time delivery")

st.write("---")
st.subheader("Historical Context")
st.write(f"Current Gold Layer Row Count: {total_rows}")