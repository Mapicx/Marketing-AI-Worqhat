import pandas as pd
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
import joblib

def ensure_feature_columns(df, required_features):
    """Ensure the dataframe has all required feature columns"""
    for feature in required_features:
        if feature not in df.columns:
            df[feature] = 0
    return df[required_features]

def simulate_campaign(campaign, customer_segment, segment_df, response_model, required_features):
    """Simulate campaign outcomes for a segment"""
    segment_customers = segment_df[segment_df['segment'] == customer_segment]
    
    # Generate features for prediction
    campaign_data = {
        'campaign_type': campaign['type'],
        'offer_type': campaign['offer_type'],
        'target_segment': campaign['target_segment'],
        'discount_pct': campaign['discount'],
        'budget': campaign['budget'],
        'target_size': len(segment_customers)
    }
    
    # Convert to DataFrame for prediction
    campaign_df = pd.DataFrame([campaign_data])
    campaign_df = pd.get_dummies(campaign_df)
    
    # Ensure all columns are present
    campaign_df = ensure_feature_columns(campaign_df, required_features)
    
    # Predict response rate
    predicted_success = response_model.predict_proba(campaign_df)[0][1]
    
    # Simulate outcomes
    np.random.seed(42)
    conversions = np.random.binomial(1, predicted_success, len(segment_customers))
    conversion_rate = conversions.mean()
    
    # Calculate ROI (simplified)
    avg_order_value = segment_customers['total_spent'].mean() / segment_customers['purchase_frequency'].mean()
    revenue = conversion_rate * len(segment_customers) * avg_order_value
    roi = (revenue - campaign['budget']) / campaign['budget']
    
    return {
        'conversion_rate': conversion_rate,
        'revenue': revenue,
        'roi': roi,
        'predicted_success': predicted_success
    }

def ab_test(campaignA, campaignB, customer_segment, segment_df, response_model, required_features, confidence=0.95):
    """Run A/B test between two campaign variants"""
    resultsA = simulate_campaign(campaignA, customer_segment, segment_df, response_model, required_features)
    resultsB = simulate_campaign(campaignB, customer_segment, segment_df, response_model, required_features)
    
    # Statistical significance test
    n = len(segment_df[segment_df['segment'] == customer_segment])
    conversionsA = int(resultsA['conversion_rate'] * n)
    conversionsB = int(resultsB['conversion_rate'] * n)
    
    # Chi-squared test
    contingency_table = [
        [conversionsA, n - conversionsA],
        [conversionsB, n - conversionsB]
    ]
    
    chi2, p_value, _, _ = stats.chi2_contingency(contingency_table)
    significant = p_value < (1 - confidence) # type: ignore
    
    # Determine winner
    winner = 'A' if resultsA['conversion_rate'] > resultsB['conversion_rate'] else 'B'
    
    return {
        'variantA': resultsA,
        'variantB': resultsB,
        'p_value': p_value,
        'significant': significant,
        'winner': winner
    }