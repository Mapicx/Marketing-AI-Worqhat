import pandas as pd
import numpy as np
from faker import Faker

def generate_customer_data(num_customers=1000):
    fake = Faker()
    np.random.seed(42)
    
    data = {
        'customer_id': [f'C{str(i).zfill(4)}' for i in range(num_customers)],
        'age': np.random.randint(18, 70, num_customers),
        'gender': np.random.choice(['M', 'F', 'Other'], num_customers, p=[0.48, 0.5, 0.02]),
        'income': np.random.lognormal(10, 0.4, num_customers).astype(int),
        'location': [fake.city() for _ in range(num_customers)],
        'joined_date': [fake.date_between(start_date='-5y', end_date='today') for _ in range(num_customers)],
        'email': [fake.email() for _ in range(num_customers)],
        'phone': [fake.phone_number() for _ in range(num_customers)],
        'total_spent': np.random.exponential(500, num_customers).astype(int),
        'purchase_frequency': np.random.poisson(3, num_customers),
        'last_purchase_days': np.random.randint(1, 365, num_customers),
        'preferred_category': np.random.choice(
            ['Electronics', 'Fashion', 'Home', 'Beauty', 'Sports'], 
            num_customers,
            p=[0.3, 0.25, 0.2, 0.15, 0.1]
        )
    }
    
    # Add 5% outliers
    outlier_indices = np.random.choice(num_customers, int(num_customers*0.05), replace=False)
    data['total_spent'][outlier_indices] = np.random.randint(10000, 50000, len(outlier_indices))
    data['purchase_frequency'][outlier_indices] = np.random.randint(50, 100, len(outlier_indices))
    
    return pd.DataFrame(data)

def generate_campaign_history(num_campaigns=200):
    fake = Faker()
    np.random.seed(42)
    
    data = {
        'campaign_id': [f'CAM{str(i).zfill(3)}' for i in range(num_campaigns)],
        'campaign_type': np.random.choice(
            ['Email', 'Social', 'Push', 'SMS', 'Direct Mail'], 
            num_campaigns,
            p=[0.4, 0.3, 0.15, 0.1, 0.05]
        ),
        'target_segment': np.random.choice(['All', 'Young', 'HighIncome', 'Frequent'], num_campaigns),
        'offer_type': np.random.choice(
            ['Discount', 'Bundle', 'Free Shipping', 'Cashback', 'Gift'], 
            num_campaigns
        ),
        'discount_pct': np.random.uniform(5, 50, num_campaigns).round(1),
        'duration_days': np.random.randint(3, 30, num_campaigns),
        'budget': np.random.uniform(500, 20000, num_campaigns).round(2),
        'target_size': np.random.randint(100, 10000, num_campaigns),
        'conversion_rate': np.random.beta(2, 50, num_campaigns).round(4),
        'roi': np.random.uniform(0.5, 5.0, num_campaigns).round(2),
        'success': np.random.choice([0, 1], num_campaigns, p=[0.4, 0.6])
    }
    
    # Calculate revenue based on conversion rate and target size
    avg_order_value = np.random.normal(150, 50, num_campaigns)
    data['revenue'] = (data['conversion_rate'] * data['target_size'] * avg_order_value).round(2)
    
    return pd.DataFrame(data)

def generate_product_data(num_products=50):
    categories = ['Electronics', 'Fashion', 'Home', 'Beauty', 'Sports']
    data = {
        'product_id': [f'P{str(i).zfill(3)}' for i in range(num_products)],
        'product_name': [f"Product {i}" for i in range(num_products)],
        'category': [categories[i % len(categories)] for i in range(num_products)],
        'price': np.random.uniform(10, 500, num_products).round(2),
        'rating': np.random.uniform(3.0, 5.0, num_products).round(1)
    }
    return pd.DataFrame(data)

def generate_interaction_data(customers, products, num_interactions=5000):
    np.random.seed(42)
    data = {
        'customer_id': np.random.choice(customers['customer_id'], num_interactions),
        'product_id': np.random.choice(products['product_id'], num_interactions),
        'rating': np.random.randint(1, 6, num_interactions),
        'timestamp': pd.date_range(start='2023-01-01', periods=num_interactions, freq='H')
    }
    return pd.DataFrame(data)

if __name__ == "__main__":
    # Generate sample datasets
    customers = generate_customer_data()
    campaigns = generate_campaign_history()
    products = generate_product_data()
    interactions = generate_interaction_data(customers, products)
    
    # Save to CSV
    customers.to_csv('data/customers.csv', index=False)
    campaigns.to_csv('data/campaign_history.csv', index=False)
    products.to_csv('data/products.csv', index=False)
    interactions.to_csv('data/interactions.csv', index=False)
    
    print("Datasets generated and saved to data/ directory")