import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA

def analyze_customer_data(customer_df):
    """Analyze and segment customers"""
    # Create reports directory if it doesn't exist
    os.makedirs('reports', exist_ok=True)
    
    # Preprocessing
    df = customer_df.copy()
    df = df.dropna()
    
    # Feature selection
    features = df[['age', 'income', 'total_spent', 'purchase_frequency', 'last_purchase_days']]
    scaler = StandardScaler()
    scaled_features = scaler.fit_transform(features)
    
    # Dimensionality reduction for visualization
    pca = PCA(n_components=2)
    principal_components = pca.fit_transform(scaled_features)
    df['pca1'] = principal_components[:, 0]
    df['pca2'] = principal_components[:, 1]
    
    # Determine optimal clusters
    wcss = []
    for i in range(1, 11):
        kmeans = KMeans(n_clusters=i, init='k-means++', random_state=42)
        kmeans.fit(scaled_features)
        wcss.append(kmeans.inertia_)
    
    # Find elbow point (simplified)
    optimal_clusters = 4
    
    # Apply clustering
    kmeans = KMeans(n_clusters=optimal_clusters, random_state=42)
    df['segment'] = kmeans.fit_predict(scaled_features)
    
    # Analyze segments
    segment_insights = df.groupby('segment').agg({
        'age': 'mean',
        'income': 'mean',
        'total_spent': 'mean',
        'purchase_frequency': 'mean',
        'last_purchase_days': 'mean'
    }).reset_index()
    
    # Visualization
    plt.figure(figsize=(10, 6))
    sns.scatterplot(data=df, x='pca1', y='pca2', hue='segment', palette='viridis')
    plt.title('Customer Segmentation')
    plt.savefig('reports/segmentation_visualization.png')
    plt.close()
    
    return df, segment_insights.to_dict()

def analyze_campaign_data(campaign_df):
    """Analyze historical campaign patterns"""
    # Create reports directory if it doesn't exist
    os.makedirs('reports', exist_ok=True)
    
    # Basic analysis
    campaign_analysis = {
        'success_rate': campaign_df['success'].mean(),
        'avg_roi': campaign_df['roi'].mean(),
        'best_performing_type': campaign_df.groupby('campaign_type')['success'].mean().idxmax(),
        'best_performing_offer': campaign_df.groupby('offer_type')['roi'].mean().idxmax()
    }
    
    # Visualization
    plt.figure(figsize=(12, 6))
    sns.barplot(
        x='campaign_type', 
        y='conversion_rate', 
        hue='offer_type', 
        data=campaign_df,
        errorbar=None
    )
    plt.title('Conversion Rate by Campaign Type and Offer')
    plt.savefig('reports/campaign_analysis.png')
    plt.close()
    
    return campaign_analysis

if __name__ == "__main__":
    # Test with sample data
    customers = pd.read_csv('data/customers.csv')
    campaigns = pd.read_csv('data/campaign_history.csv')
    
    segmented_customers, insights = analyze_customer_data(customers)
    campaign_insights = analyze_campaign_data(campaigns)
    
    print("Customer Insights:", insights)
    print("\nCampaign Insights:", campaign_insights)