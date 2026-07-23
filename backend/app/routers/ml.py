from fastapi import APIRouter

from app.ml import ml_service
from app.models.schemas import AnalyzeRequest

router = APIRouter(prefix="/api/ml", tags=["ml"])


@router.post("/predict")
async def predict(payload: AnalyzeRequest):
    return ml_service.predict(payload.url)


@router.get("/metrics")
async def metrics():
    return ml_service.get_training_metrics()
