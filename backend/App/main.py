from fastapi import FastAPI
from App.routes import (
    img_routes, slogan_routes,
    predictive_routes,
)

app = FastAPI(title="Marketing ML API", version="1.0")

# Existing
app.include_router(img_routes.router, prefix="/img", tags=["Image Generation"])
app.include_router(slogan_routes.router, prefix="/slogan", tags=["Slogan Generation"])

# New
app.include_router(predictive_routes.router, prefix="/predictive", tags=["Predictive Analytics"])
