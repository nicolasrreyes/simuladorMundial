from fastapi import APIRouter

from app.schemas.metrics import DashboardMetrics
from app.services.metrics_service import MetricsService


router = APIRouter(prefix="/metrics", tags=["Metricas"])


@router.get("/dashboard", response_model=DashboardMetrics)
def get_dashboard_metrics():
    return MetricsService().get_dashboard_metrics()
