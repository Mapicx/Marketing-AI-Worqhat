from fastapi import FastAPI, UploadFile, File
from App.routes import (
    img_routes, slogan_routes
)
import shutil
import os
import logging
import traceback
from fastapi import APIRouter
from App.marketing_ai import main

app = FastAPI(title="Marketing ML API", version="1.0")
router = APIRouter()  # <-- This must be present

# Existing routes
app.include_router(img_routes.router, prefix="/img", tags=["Image Generation"])
app.include_router(slogan_routes.router, prefix="/slogan", tags=["Slogan Generation"])

# Custom /forecast endpoint that runs main.py
DATA_DIR = r"D:\TechNeeti\marketing_ai_platform\data"

@router.post("/forecast", tags=["Predictive Analytics"])
async def forecast(file1: UploadFile = File(...), file2: UploadFile = File(...)):
    """Endpoint to run predictive marketing analytics on uploaded customer and campaign data"""
    os.makedirs(DATA_DIR, exist_ok=True)
    
    response = {
        'status': 'processing',
        'logs': [],
        'results': None,
        'error': None
    }
    
    try:
        response['logs'].append(f"Received files: {file1.filename}, {file2.filename}")
        file1_path = os.path.join(DATA_DIR, file1.filename) # type: ignore
        file2_path = os.path.join(DATA_DIR, file2.filename) # type: ignore
        with open(file1_path, "wb") as f:
            shutil.copyfileobj(file1.file, f)
        with open(file2_path, "wb") as f:
            shutil.copyfileobj(file2.file, f)
        response['logs'].append(f"Files saved to: {file1_path}, {file2_path}")
        results = main.main(csv1=file1_path, csv2=file2_path)
        response['status'] = results['status']
        response['results'] = {
            'segment_count': results.get('segment_count'),
            'recommended_campaign_type': results.get('recommended_campaign_type'),
            'recommended_offer': results.get('recommended_offer'),
            'success_probability': results.get('success_probability'),
            'privacy_compliance': results.get('privacy_compliance'),
            'campaign_details': results.get('campaign_details'),
            'report_path': results.get('report_path'),
            'pdf_url': results.get('pdf_url')
        }
        response['logs'] += results.get('logs', [])
        return response
    except Exception as e:
        error_msg = f"Processing failed: {str(e)}"
        stack_trace = traceback.format_exc()
        response['status'] = 'error'
        response['error'] = error_msg
        response['logs'].append(error_msg)
        response['logs'].append(f"Stack trace: {stack_trace}")
        logging.error(error_msg)
        logging.error(stack_trace)
        return response