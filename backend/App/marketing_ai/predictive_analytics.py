import pandas as pd
import numpy as np
import os
import joblib
import matplotlib.pyplot as plt
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, mean_absolute_error

def ensure_feature_columns(df, required_features):
    """Ensure the dataframe has all required feature columns"""
    for feature in required_features:
        if feature not in df.columns:
            df[feature] = 0
    return df[required_features]

def build_roi_forecast_model(campaign_df):
    """Build model to forecast campaign ROI"""
    # Create models directory if it doesn't exist
    os.makedirs('models', exist_ok=True)
    
    # Feature engineering
    X = campaign_df[['campaign_type', 'offer_type', 'target_segment', 'discount_pct', 'budget', 'target_size']]
    y = campaign_df['roi']
    
    # Convert categorical features
    X = pd.get_dummies(X, columns=['campaign_type', 'offer_type', 'target_segment'])
    
    # Save feature names
    feature_names = X.columns.tolist()
    
    # Train/test split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    
    # Train model
    model = GradientBoostingRegressor(n_estimators=150, learning_rate=0.1, max_depth=3, random_state=42)
    model.fit(X_train, y_train)
    
    # Evaluate
    y_pred = model.predict(X_test)
    r2 = r2_score(y_test, y_pred)
    mae = mean_absolute_error(y_test, y_pred)
    
    # Visualization
    try:
        plt.figure(figsize=(10, 6))
        plt.scatter(y_test, y_pred, alpha=0.5)
        plt.plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()], 'k--')
        plt.xlabel('Actual ROI')
        plt.ylabel('Predicted ROI')
        plt.title('ROI Prediction Accuracy')
        plt.savefig('reports/roi_prediction_accuracy.png')
        plt.close()
    except Exception as e:
        print(f"Could not generate ROI visualization: {str(e)}")
    
    # Save model and feature names
    joblib.dump(model, 'models/roi_forecast_model.pkl')
    joblib.dump(feature_names, 'models/roi_model_features.pkl')
    
    return model, {'r2': r2, 'mae': mae}, feature_names

def forecast_campaign_success(campaign_features, response_model, response_features, roi_model, roi_features):
    """Predict campaign success metrics"""
    # Prepare features
    campaign_df = pd.DataFrame([campaign_features])
    campaign_df = pd.get_dummies(campaign_df)
    
    # Ensure all columns for response model
    campaign_df_resp = ensure_feature_columns(campaign_df.copy(), response_features)
    
    # Ensure all columns for ROI model
    campaign_df_roi = ensure_feature_columns(campaign_df.copy(), roi_features)
    
    # Predict success probability
    success_prob = response_model.predict_proba(campaign_df_resp)[0][1]
    
    # Predict ROI
    roi = roi_model.predict(campaign_df_roi)[0]
    
    # Business rules for success
    success = success_prob > 0.6 and roi > 1.0
    
    return {
        'success_probability': success_prob,
        'predicted_roi': roi,
        'predicted_success': success
    }

if __name__ == "__main__":
    # Test with sample data
    campaigns = pd.read_csv('data/campaign_history.csv')
    model, metrics, features = build_roi_forecast_model(campaigns)
    print("ROI Forecast Model Built")
    print("R2 Score:", metrics['r2'])
    print("MAE:", metrics['mae'])
    
    # Test prediction
    import joblib
    # For the response model, we would need to load it and its features
    # This is just a dummy test
    campaign_features = {
        'campaign_type': 'Email',
        'offer_type': 'Discount',
        'target_segment': 'HighIncome',
        'discount_pct': 20,
        'budget': 10000,
        'target_size': 5000
    }
    
    # We'll assume features are the same for this test
    prediction = forecast_campaign_success(
        campaign_features, 
        None,  # We don't have a response model here
        features,
        model,
        features
    )
    print("\nCampaign Prediction:", prediction)