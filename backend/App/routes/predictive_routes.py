from fastapi import APIRouter
from App.marketing_ai import data_loader, personalization_models, predictive_analytics

router = APIRouter()

@router.get("/forecast")
def forecast_campaign():
    campaigns = data_loader.generate_campaign_history(100)
    resp_model, _, resp_features = personalization_models.build_response_prediction_model(campaigns)
    roi_model, roi_metrics, roi_features = predictive_analytics.build_roi_forecast_model(campaigns)

    campaign = {
        "campaign_type": "Email",
        "offer_type": "Discount",
        "target_segment": "HighIncome",
        "discount_pct": 20,
        "budget": 8000,
        "target_size": 5000,
    }
    prediction = predictive_analytics.forecast_campaign_success(campaign, resp_model, resp_features, roi_model, roi_features)
    return {"prediction": prediction, "roi_metrics": roi_metrics}
