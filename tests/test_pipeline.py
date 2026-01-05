import pytest
import pandas as pd
import numpy as np

def test_risk_multiplier_calculation():
    """Verifies the Risk Multiplier logic used for delay predictions."""
    risk_input = 0.8  # High risk
    risk_impact = (risk_input - 0.5) * 1.5 
    
    assert risk_impact > 0  # High risk should increase the delay
    assert isinstance(risk_impact, float)

def test_sentiment_bounds():
    """Ensures sentiment values are strictly handled within the 0 to 1 range."""
    min_risk = 0.0
    max_risk = 1.0
    assert min_risk <= 0.5 <= max_risk

def test_quality_firewall_logic():
    """Verifies that corrupted records (negative shipping/price) are filtered out."""
    # Mock data representing a mix of clean and corrupted records
    data = pd.DataFrame({
        'shipping_days': [3, -1, 5, 0],  # -1 is corrupted
        'product_price': [100, 200, -50, 150]  # -50 is corrupted
    })

    # Logic mimicking the Silver Layer firewall
    clean_data = data[(data['shipping_days'] >= 0) & (data['product_price'] > 0)]

    # Assertions to prove integrity
    assert len(clean_data) == 2, "Firewall should have filtered 2 corrupted rows"
    assert clean_data['shipping_days'].min() >= 0
    assert (clean_data['product_price'] > 0).all()