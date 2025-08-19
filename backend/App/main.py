from fastapi import FastAPI
from App.routes import img_routes, slogan_routes
from App.routes.predictive_routes import router as predictive_router
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = FastAPI(title="Marketing ML API", version="1.0")

app.include_router(img_routes.router, prefix="/img", tags=["Image Generation"])
app.include_router(slogan_routes.router, prefix="/slogan", tags=["Slogan Generation"])
app.include_router(predictive_router, tags=["Predictive Analytics"])