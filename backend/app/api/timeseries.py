"""
API Routes - Time Series endpoint.
Provides operational forecasting using the Forecasting Engine.
"""
from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List
from ..models import CapacityForecast, RiskEvent
from ..services.forecasting_engine import get_forecaster, ForecastTarget

router = APIRouter(prefix="/timeseries", tags=["Time Series Forecasting"])


@router.get("/forecast/{target}", response_model=CapacityForecast)
async def get_forecast(target: str, hours: int = 24) -> CapacityForecast:
    """
    Get time-series forecast for a specific operational metric.
    
    Args:
        target: One of 'icu_occupancy', 'er_arrivals', 'ward_occupancy'
        hours: Forecast horizon in hours (default 24)
    """
    try:
        forecast_target = ForecastTarget(target)
    except ValueError:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid target. Must be one of: {[t.value for t in ForecastTarget]}"
        )
    
    forecaster = get_forecaster()
    return forecaster.forecast(forecast_target, horizon_hours=hours)


@router.get("/forecasts/all")
async def get_all_forecasts(hours: int = 24) -> Dict[str, CapacityForecast]:
    """
    Get forecasts for all operational metrics.
    
    Returns forecasts for ICU occupancy, ER arrivals, and Ward occupancy.
    """
    forecaster = get_forecaster()
    return forecaster.get_all_forecasts(horizon_hours=hours)


@router.get("/capacity/summary")
async def get_capacity_summary() -> Dict[str, Any]:
    """
    Get current capacity status across all metrics.
    
    Returns:
        - Current values for each metric
        - Status (normal/warning/critical)
        - Active alerts
    """
    forecaster = get_forecaster()
    return forecaster.get_capacity_summary()


@router.get("/alerts", response_model=List[RiskEvent])
async def get_active_alerts() -> List[RiskEvent]:
    """
    Get currently active capacity alerts based on forecasts.
    
    Checks all metrics against thresholds and returns triggered alerts.
    """
    forecaster = get_forecaster()
    all_alerts = []
    
    for target in ForecastTarget:
        forecast = forecaster.forecast(target, horizon_hours=6)
        alerts = forecaster.check_thresholds(forecast)
        all_alerts.extend(alerts)
    
    return all_alerts


@router.get("/thresholds")
async def get_thresholds() -> Dict[str, Any]:
    """
    Get configured alert thresholds for all metrics.
    """
    from ..services.forecasting_engine import THRESHOLDS
    
    return {
        target.value: {
            "warning": config.warning,
            "critical": config.critical,
            "unit": config.unit,
        }
        for target, config in THRESHOLDS.items()
    }


@router.get("/targets")
async def list_forecast_targets() -> Dict[str, Any]:
    """
    List available forecast targets with descriptions.
    """
    return {
        "targets": [
            {
                "name": ForecastTarget.ICU_OCCUPANCY.value,
                "description": "ICU bed occupancy percentage",
                "unit": "%",
            },
            {
                "name": ForecastTarget.ER_ARRIVALS.value,
                "description": "Emergency room patient arrivals per hour",
                "unit": "patients/hr",
            },
            {
                "name": ForecastTarget.WARD_OCCUPANCY.value,
                "description": "General ward bed occupancy percentage",
                "unit": "%",
            },
        ]
    }


@router.get("/status")
async def timeseries_status() -> Dict[str, Any]:
    """Get time series engine status."""
    return {
        "status": "operational",
        "engine": "ARIMA + Seasonality Decomposition",
        "targets_available": [t.value for t in ForecastTarget],
        "features": {
            "arima_forecasting": True,
            "daily_seasonality": True,
            "weekly_seasonality": True,
            "confidence_intervals": True,
            "threshold_alerting": True,
        }
    }
