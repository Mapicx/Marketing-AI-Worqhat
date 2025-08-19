import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def anonymize_data(df, columns_to_protect):
    """Anonymize sensitive data in specified columns"""
    if not isinstance(df, pd.DataFrame) or df.empty:
        logger.warning("Invalid or empty DataFrame passed to anonymize_data")
        return df
        
    anonymized_df = df.copy()
    
    for col in columns_to_protect:
        if col not in anonymized_df.columns:
            logger.warning(f"Column '{col}' not found for anonymization")
            continue
            
        if col == 'email' and anonymized_df[col].dtype == 'object':
            try:
                domain = anonymized_df[col].str.split('@').str[1]
                anonymized_df[col] = 'user_' + anonymized_df.index.astype(str) + '@' + domain
            except Exception as e:
                logger.error(f"Error anonymizing emails: {str(e)}")
                
        elif col == 'phone' and anonymized_df[col].dtype == 'object':
            try:
                # Handle various phone formats
                anonymized_df[col] = anonymized_df[col].apply(
                    lambda x: 'XXX-XXX-' + str(x)[-4:] if pd.notnull(x) else x
                )
            except Exception as e:
                logger.error(f"Error anonymizing phones: {str(e)}")
                
        elif col == 'name' and anonymized_df[col].dtype == 'object':
            try:
                anonymized_df[col] = 'Customer_' + anonymized_df.index.astype(str)
            except Exception as e:
                logger.error(f"Error anonymizing names: {str(e)}")
    
    return anonymized_df

def handle_outliers(df, numerical_columns, method='isolation_forest'):
    """Detect and handle outliers in numerical columns"""
    if not isinstance(df, pd.DataFrame) or df.empty:
        logger.warning("Invalid or empty DataFrame passed to handle_outliers")
        return df
        
    # Filter to existing numerical columns
    existing_cols = [col for col in numerical_columns 
                    if col in df.columns and pd.api.types.is_numeric_dtype(df[col])]
    
    if not existing_cols:
        logger.warning("No valid numerical columns for outlier detection")
        return df
        
    logger.info(f"Processing outliers in columns: {existing_cols}")
    cleaned_df = df.copy()
    
    if method == 'isolation_forest':
        try:
            # Train Isolation Forest
            clf = IsolationForest(contamination=0.05, random_state=42, n_jobs=-1)
            clf.fit(cleaned_df[existing_cols])
            
            # Identify outliers
            outliers = clf.predict(cleaned_df[existing_cols]) == -1
            logger.info(f"Identified {outliers.sum()} outliers using Isolation Forest")
            
            # Replace outliers with median instead of removing
            for col in existing_cols:
                median_val = cleaned_df[col].median()
                cleaned_df.loc[outliers, col] = median_val
                
        except Exception as e:
            logger.error(f"Isolation Forest failed: {str(e)}")
            return df
            
    elif method == 'iqr':
        try:
            for col in existing_cols:
                q1 = cleaned_df[col].quantile(0.25)
                q3 = cleaned_df[col].quantile(0.75)
                iqr = q3 - q1
                
                if iqr == 0:  # Skip if no variability
                    continue
                    
                lower_bound = q1 - 1.5 * iqr
                upper_bound = q3 + 1.5 * iqr
                
                # Calculate outliers
                outliers = (cleaned_df[col] < lower_bound) | (cleaned_df[col] > upper_bound)
                logger.info(f"Column '{col}': {outliers.sum()} IQR outliers")
                
                # Replace outliers with median
                median_val = cleaned_df[col].median()
                cleaned_df.loc[outliers, col] = median_val
                
        except Exception as e:
            logger.error(f"IQR method failed: {str(e)}")
            return df
    
    return cleaned_df

def handle_missing_data(df, strategy='median'):
    """Handle missing values in dataset"""
    if not isinstance(df, pd.DataFrame) or df.empty:
        logger.warning("Invalid or empty DataFrame passed to handle_missing_data")
        return df
        
    cleaned_df = df.copy()
    missing_counts = cleaned_df.isnull().sum()
    total_missing = missing_counts.sum()
    
    if total_missing == 0:
        logger.info("No missing values found")
        return cleaned_df
        
    logger.info(f"Handling {total_missing} missing values using '{strategy}' strategy")
    
    for col in cleaned_df.columns:
        col_missing = cleaned_df[col].isnull().sum()
        if col_missing == 0:
            continue
            
        logger.info(f"Column '{col}': {col_missing} missing values")
        
        if pd.api.types.is_numeric_dtype(cleaned_df[col]):
            if strategy == 'median':
                fill_value = cleaned_df[col].median()
            elif strategy == 'mean':
                fill_value = cleaned_df[col].mean()
            elif strategy == 'drop':
                cleaned_df = cleaned_df.dropna(subset=[col])
                logger.info(f"Dropped {col_missing} rows with missing '{col}'")
                continue
            else:  # Default to zero
                fill_value = 0
                
            cleaned_df[col].fillna(fill_value, inplace=True)
            
        else:  # Handle non-numeric columns
            if strategy == 'drop':
                cleaned_df = cleaned_df.dropna(subset=[col])
                logger.info(f"Dropped {col_missing} rows with missing '{col}'")
            else:  # Mode imputation for categorical
                mode_value = cleaned_df[col].mode()[0] if not cleaned_df[col].mode().empty else 'Unknown'
                cleaned_df[col].fillna(mode_value, inplace=True)
    
    return cleaned_df

if __name__ == "__main__":
    # Create test data
    test_data = {
        'customer_id': [f'C{i:04d}' for i in range(10)],
        'age': [25, 32, None, 45, 150, 29, 38, 41, 28, 33],  # 150 is outlier
        'income': [50000, 75000, 62000, None, 230000, 58000, 71000, 68000, 54000, 120000],
        'email': [
            'user1@example.com', 
            'user2@domain.net', 
            None, 
            'user4@test.org', 
            'invalid-email', 
            'user6@company.com', 
            'user7@example.com', 
            None, 
            'user9@domain.com', 
            'user10@test.io'
        ],
        'phone': [
            '123-456-7890', 
            '555-1234', 
            '0987654321', 
            None, 
            'invalid-phone', 
            '555-987-6543', 
            '1234567890', 
            '555-5555', 
            None, 
            '888-999-0000'
        ]
    }
    
    test_df = pd.DataFrame(test_data)
    print("Original Test Data:")
    print(test_df)
    print("\nMissing values:")
    print(test_df.isnull().sum())
    
    # Test anonymization
    anonymized = anonymize_data(test_df, ['email', 'phone', 'name'])
    print("\nAnonymized Data:")
    print(anonymized[['customer_id', 'email', 'phone']])
    
    # Test outlier handling
    outlier_cols = ['age', 'income', 'non_existent_column']
    cleaned = handle_outliers(anonymized, outlier_cols, method='isolation_forest')
    print("\nAfter Outlier Handling (Isolation Forest):")
    print(cleaned[['customer_id', 'age', 'income']])
    
    # Test missing data handling
    missing_handled = handle_missing_data(cleaned, strategy='median')
    print("\nAfter Missing Data Handling:")
    print(missing_handled)
    print("\nFinal Missing values:")
    print(missing_handled.isnull().sum())