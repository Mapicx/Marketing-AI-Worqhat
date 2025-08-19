from fastapi import FastAPI
from App.routes import img_routes, slogan_routes , rag_routes
from App.routes.predictive_routes import router as predictive_router
import logging
from fastapi.middleware.cors import CORSMiddleware

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = FastAPI(title="Marketing ML API", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*","http://localhost:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(img_routes.router, prefix="/img", tags=["Image Generation"])
app.include_router(slogan_routes.router, prefix="/slogan", tags=["Slogan Generation"])
app.include_router(predictive_router, tags=["Predictive Analytics"])
app.include_router(rag_routes.router, prefix="/rag", tags=["YouTube Summarizer"])