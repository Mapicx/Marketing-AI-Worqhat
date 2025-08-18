# main.py
import pandas as pd
from data_loader import generate_customer_data, generate_campaign_history
from data_analysis import analyze_customer_data, analyze_campaign_data
from personalization_models import build_segmentation_model, build_response_prediction_model
from campaign_simulation import ab_test
from predictive_analytics import build_roi_forecast_model, forecast_campaign_success
from edge_cases import anonymize_data, handle_outliers
from report_generator import generate_report
import joblib
import os
import time
import json

def main():
    # Step 1: Create necessary directories
    os.makedirs('reports', exist_ok=True)
    os.makedirs('models', exist_ok=True)
    
    # Step 2: Generate or load data
    print("Generating sample datasets...")
    customers = generate_customer_data(1000)
    campaigns = generate_campaign_history(200)
    
    # Step 3: Handle edge cases
    print("\nHandling edge cases...")
    customers_clean = anonymize_data(customers, ['email', 'phone'])
    customers_clean = handle_outliers(customers_clean, ['income', 'total_spent'])
    
    # Step 4: Audience research (generates images)
    print("\nAnalyzing customer data...")
    segmented_customers, segment_insights = analyze_customer_data(customers_clean)
    campaign_insights = analyze_campaign_data(campaigns)
    
    # Create analysis_results here
    analysis_results = {
        'segment_distribution': segment_insights,
        'key_segments': [0, 1, 2],
        'best_performing_type': campaign_insights['best_performing_type'],
        'best_performing_offer': campaign_insights['best_performing_offer']
    }
    
    # Step 5: Build personalization models (ROI model generates image)
    print("\nBuilding personalization models...")
    segmented_customers, seg_model = build_segmentation_model(customers_clean)
    resp_model, report, resp_features = build_response_prediction_model(campaigns)
    roi_model, roi_metrics, roi_features = build_roi_forecast_model(campaigns)
    
    # Ensure images are fully written to disk
    print("Waiting for images to be written to disk...")
    time.sleep(5)  # Increased from 2 to 3 seconds
    
    # Step 6: Campaign simulation
    print("\nRunning campaign simulations...")
    campaignA = {
        'type': 'Email',
        'offer_type': 'Gift',
        'target_segment': 'All',
        'discount': 15,
        'budget': 5000
    }
    
    campaignB = {
        'type': 'Social',
        'offer_type': 'Bundle',
        'target_segment': 'Frequent',
        'discount': 20,
        'budget': 6000
    }
    
    ab_results = ab_test(campaignA, campaignB, 1, segmented_customers, resp_model, resp_features)
    
    # Step 7: Predictive analytics
    print("\nRunning predictive analytics...")
    
    # Get recommended campaign type and offer from analysis
    recommended_type = analysis_results['best_performing_type']
    recommended_offer = analysis_results['best_performing_offer']
    
    campaign_features = {
        'campaign_type': recommended_type,
        'offer_type': recommended_offer,
        'target_segment': 'HighIncome',
        'discount_pct': 20,
        'budget': 10000,
        'target_size': 5000
    }
    
    prediction = forecast_campaign_success(
        campaign_features, 
        resp_model, 
        resp_features,
        roi_model,
        roi_features
    )
    
    # Step 8: Generate report
    print("\nGenerating business creativity report...")
    # Add predicted campaign to analysis_results
    analysis_results['predicted_campaign'] = campaign_features
    
    # Create report data with privacy compliance info
    privacy_handled = True
    report_data = {
        'privacy_compliance': {
            'handled': privacy_handled
        },
        'conversion_rate': campaign_insights.get('success_rate', 0),
        'avg_order_value': campaigns['revenue'].mean() / campaigns['target_size'].mean() 
                            if 'revenue' in campaigns else 0
    }
    
    report_data, html_report = generate_report(
        report_data=report_data,
        analysis_results=analysis_results,
        simulation_results=ab_results,
        prediction_results=prediction
    )
    
    # Save the HTML report
    report_path = 'reports/business_creativity_report.html'
    with open(report_path, 'w') as f:
        f.write(html_report)
    
    print("\n=== Report Summary ===")
    print(f"Identified {len(analysis_results['segment_distribution'])} customer segments")
    print(f"Recommended campaign type: {analysis_results['best_performing_type']}")
    print(f"Recommended campaign offer: {analysis_results['best_performing_offer']}")
    print(f"Predicted campaign success: {prediction['success_probability']:.2f}")
    print(f"Privacy compliance: {'Met' if report_data['privacy_compliance']['handled'] else 'Needs attention'}") # type: ignore
    
    # Print campaign details
    print("\nPredicted Most Successful Campaign:")
    print(f"  Type: {campaign_features['campaign_type']}")
    print(f"  Offer: {campaign_features['offer_type']}")
    print(f"  Target: {campaign_features['target_segment']}")
    print(f"  Discount: {campaign_features['discount_pct']}%")
    print(f"  Budget: ${campaign_features['budget']:,.2f}")
    print(f"  Target Size: {campaign_features['target_size']} customers")
    
    print(f"\nReport saved to {report_path}")

if __name__ == "__main__":
    # Check Cloudinary configuration
    required_envs = ['CLOUDINARY_CLOUD_NAME', 'CLOUDINARY_API_KEY', 'CLOUDINARY_API_SECRET']
    missing = [env for env in required_envs if not os.getenv(env)]
    
    if missing:
        print(f"Error: Missing Cloudinary environment variables: {', '.join(missing)}")
        print("Please set these variables before running the application.")
    else:
        main()