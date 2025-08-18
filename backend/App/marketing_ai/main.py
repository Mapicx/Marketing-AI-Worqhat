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
    
    # Step 4: Audience research
    print("\nAnalyzing customer data...")
    segmented_customers, segment_insights = analyze_customer_data(customers_clean)
    campaign_insights = analyze_campaign_data(campaigns)
    
    # Step 5: Build personalization models
    print("\nBuilding personalization models...")
    segmented_customers, seg_model = build_segmentation_model(customers_clean)
    resp_model, report, resp_features = build_response_prediction_model(campaigns)
    roi_model, roi_metrics, roi_features = build_roi_forecast_model(campaigns)  # Updated to get features
    
    # Step 6: Campaign simulation
    print("\nRunning campaign simulations...")
    campaignA = {
        'type': 'Email',
        'offer_type': 'Discount',
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
    campaign_features = {
        'campaign_type': 'Email',
        'offer_type': 'Discount',
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
    analysis_results = {
        'segment_distribution': segment_insights,
        'key_segments': [0, 1, 2],
        'best_performing_type': campaign_insights['best_performing_type'],
        'best_performing_offer': campaign_insights['best_performing_offer']
    }
    
    # Create report data with privacy compliance info
    privacy_handled = True
    report_data = {
        'privacy_compliance': {
            'handled': privacy_handled
        }
    }
    
    report_data, html_report = generate_report(
        report_data=report_data,
        analysis_results=analysis_results,
        simulation_results=ab_results,
        prediction_results=prediction
    )
    
    # Save the HTML report
    with open('reports/business_creativity_report.html', 'w') as f:
        f.write(html_report)
    
    print("\n=== Report Summary ===")
    print(f"Identified {len(analysis_results['segment_distribution'])} customer segments")
    print(f"Recommended campaign type: {analysis_results['best_performing_type']}")
    print(f"Predicted campaign success: {prediction['success_probability']:.2f}")
    print(f"Privacy compliance: {'Met' if report_data['privacy_compliance']['handled'] else 'Needs attention'}") # type: ignore
    print("\nReport saved to reports/ directory")

if __name__ == "__main__":
    main()