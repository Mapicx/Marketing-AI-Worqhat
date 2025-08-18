import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest

def anonymize_data(df, columns_to_protect):
    """Anonymize sensitive data"""
    anonymized_df = df.copy()
    
    for col in columns_to_protect:
        if col in anonymized_df.columns:
            if col == 'email':
                domain = anonymized_df[col].str.split('@').str[1]
                anonymized_df[col] = 'user_' + anonymized_df.index.astype(str) + '@' + domain
            elif col == 'phone':
                anonymized_df[col] = 'XXX-XXX-' + anonymized_df[col].str[-4:]
            elif col == 'name':
                anonymized_df[col] = 'Customer_' + anonymized_df.index.astype(str)
    
    return anonymized_df

def handle_outliers(df, numerical_columns, method='isolation_forest'):
    """Detect and handle outliers"""
    cleaned_df = df.copy()
    
    if method == 'isolation_forest':
        # Train Isolation Forest
        clf = IsolationForest(contamination=0.05, random_state=42)
        clf.fit(df[numerical_columns])
        
        # Identify outliers
        outliers = clf.predict(df[numerical_columns]) == -1
        cleaned_df = cleaned_df[~outliers]
        
    elif method == 'iqr':
        # IQR method for each column
        for col in numerical_columns:
            q1 = df[col].quantile(0.25)
            q3 = df[col].quantile(0.75)
            iqr = q3 - q1
            lower_bound = q1 - 1.5 * iqr
            upper_bound = q3 + 1.5 * iqr
            
            cleaned_df = cleaned_df[
                (cleaned_df[col] >= lower_bound) & 
                (cleaned_df[col] <= upper_bound)
            ]
    
    return cleaned_df

def handle_missing_data(df, strategy='median'):
    """Handle missing values in dataset"""
    cleaned_df = df.copy()
    
    for col in cleaned_df.columns:
        if cleaned_df[col].dtype in ['int64', 'float64']:
            if strategy == 'median':
                cleaned_df[col].fillna(cleaned_df[col].median(), inplace=True)
            elif strategy == 'mean':
                cleaned_df[col].fillna(cleaned_df[col].mean(), inplace=True)
            elif strategy == 'drop':
                cleaned_df.dropna(subset=[col], inplace=True)
        else:
            cleaned_df[col].fillna(cleaned_df[col].mode()[0], inplace=True)
    
    return cleaned_df

if __name__ == "__main__":
    # Test with sample data
    customers = pd.read_csv('data/customers.csv')
    
    # Anonymize data
    anonymized = anonymize_data(customers, ['email', 'phone'])
    print("Anonymized data sample:")
    print(anonymized[['customer_id', 'email', 'phone']].head())
    
    # Handle outliers
    numerical_cols = ['age', 'income', 'total_spent', 'purchase_frequency']
    cleaned = handle_outliers(customers, numerical_cols)
    print(f"\nOriginal rows: {len(customers)}, After outlier removal: {len(cleaned)}")
    
    # Handle missing data (create some missing values for demo)
    customers_missing = customers.copy()
    for col in numerical_cols:
        customers_missing.loc[customers_missing.sample(frac=0.1).index, col] = np.nan
    
    cleaned_missing = handle_missing_data(customers_missing)
    print(f"Missing values handled. Original missing: {customers_missing.isna().sum().sum()}, After: {cleaned_missing.isna().sum().sum()}")