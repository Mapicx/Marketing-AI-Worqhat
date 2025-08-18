import pandas as pd
import numpy as np
import os
import joblib
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import NearestNeighbors
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report

def build_segmentation_model(customer_df):
    """Build customer segmentation model"""
    # Create models directory if it doesn't exist
    os.makedirs('models', exist_ok=True)
    
    features = customer_df[['age', 'income', 'total_spent', 'purchase_frequency', 'last_purchase_days']]
    scaler = StandardScaler()
    scaled_features = scaler.fit_transform(features)
    
    kmeans = KMeans(n_clusters=5, random_state=42)
    customer_df['segment'] = kmeans.fit_predict(scaled_features)
    
    # Save models
    joblib.dump(scaler, 'models/scaler.pkl')
    joblib.dump(kmeans, 'models/segmentation_model.pkl')
    
    return customer_df, kmeans

def build_recommendation_model(interaction_df, product_df):
    """Build product recommendation model"""
    # Create models directory if it doesn't exist
    os.makedirs('models', exist_ok=True)
    
    # Create user-item matrix
    user_item_matrix = interaction_df.pivot_table(
        index='customer_id', 
        columns='product_id', 
        values='rating', 
        fill_value=0
    )
    
    # KNN model for collaborative filtering
    model = NearestNeighbors(n_neighbors=5, metric='cosine', algorithm='brute')
    model.fit(user_item_matrix)
    
    # Save model
    joblib.dump(model, 'models/recommendation_model.pkl')
    
    return model, user_item_matrix

def build_response_prediction_model(campaign_df):
    """Build model to predict campaign response"""
    # Create models directory if it doesn't exist
    os.makedirs('models', exist_ok=True)
    
    # Feature engineering
    X = campaign_df[['campaign_type', 'offer_type', 'target_segment', 'discount_pct', 'budget', 'target_size']]
    y = campaign_df['success']
    
    # Convert categorical features
    X = pd.get_dummies(X, columns=['campaign_type', 'offer_type', 'target_segment'])
    
    # Save feature names
    feature_names = X.columns.tolist()
    
    # Train/test split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    
    # Train model
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    
    # Evaluate
    y_pred = model.predict(X_test)
    report = classification_report(y_test, y_pred, output_dict=True)
    
    # Save model and feature names
    joblib.dump(model, 'models/response_prediction_model.pkl')
    joblib.dump(feature_names, 'models/response_model_features.pkl')
    
    return model, report, feature_names  # Return three values


def generate_personalized_offer(customer_id, segment, model, user_item_matrix, products):
    """Generate personalized offer for customer"""
    # For demo purposes - in real system would use model
    if segment == 0:  # High-value customers
        return {"offer_type": "Premium Bundle", "discount": 20}
    elif segment == 1:  # Frequent shoppers
        return {"offer_type": "Loyalty Discount", "discount": 15}
    elif segment == 2:  # New customers
        return {"offer_type": "Welcome Offer", "discount": 25}
    else:
        return {"offer_type": "Seasonal Offer", "discount": 10}

if __name__ == "__main__":
    # Test with sample data
    customers = pd.read_csv('data/customers.csv')
    interactions = pd.read_csv('data/interactions.csv')
    products = pd.read_csv('data/products.csv')
    campaigns = pd.read_csv('data/campaign_history.csv')
    
    # Build models - update this call too
    segmented_customers, seg_model = build_segmentation_model(customers)
    rec_model, user_item_matrix = build_recommendation_model(interactions, products)
    resp_model, report, feature_names = build_response_prediction_model(campaigns)  # Updated
    
    print("Segmentation model built")
    print("Recommendation model built")
    print("Response prediction model built")
    print("Classification Report:\n", report)