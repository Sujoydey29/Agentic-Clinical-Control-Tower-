"""
API Routes - Forecasting endpoint.
Provides capacity forecasts using the MIMIC-IV Replay Engine.
"""
from fastapi import APIRouter
from typing import List, Dict, Any
from ..models import CapacityForecast, RiskEvent
from ..services.simulation_engine import get_replay_engine
from datetime import datetime
import uuid

router = APIRouter(prefix="/forecasts", tags=["Forecasting"])


@router.get("/icu-occupancy", response_model=CapacityForecast)
async def get_icu_forecast(hours: int = 24):
    """
    Get ICU occupancy forecast with confidence intervals.
    Based on MIMIC-IV historical patterns.
    
    Args:
        hours: Forecast horizon in hours (default 24)
    """
    engine = get_replay_engine()
    return engine.get_icu_occupancy_forecast(hours=hours)


@router.get("/er-arrivals", response_model=CapacityForecast)
async def get_er_arrivals_forecast(hours: int = 24):
    """
    Get ER arrivals forecast based on time-of-day patterns.
    
    Args:
        hours: Forecast horizon in hours (default 24)
    """
    engine = get_replay_engine()
    return engine.get_er_arrivals_forecast(hours=hours)


@router.get("/ward-occupancy", response_model=CapacityForecast)
async def get_ward_forecast(hours: int = 24):
    """
    Get general ward occupancy forecast.
    """
    engine = get_replay_engine()
    # Reuse ER logic with different base levels
    forecast = engine.get_icu_occupancy_forecast(hours=hours)
    forecast.metric_name = "ward_occupancy"
    # Adjust values for ward (typically lower than ICU)
    for dp in forecast.data_points:
        dp.predicted_value = max(40, dp.predicted_value - 15)
        dp.lower_bound = max(30, dp.lower_bound - 15)
        dp.upper_bound = max(50, dp.upper_bound - 15)
    return forecast


@router.get("/summary")
async def get_forecast_summary() -> Dict[str, Any]:
    """
    Get summary of all current forecasts and capacity status.
    """
    engine = get_replay_engine()
    
    icu = engine.get_icu_occupancy_forecast(hours=6)
    er = engine.get_er_arrivals_forecast(hours=6)
    
    def get_status(current: float, critical: float, warning: float) -> str:
        if current >= critical:
            return "critical"
        elif current >= warning:
            return "warning"
        return "normal"
    
    icu_current = icu.data_points[0].predicted_value if icu.data_points else 0
    er_current = er.data_points[0].predicted_value if er.data_points else 0
    
    return {
        "timestamp": datetime.utcnow().isoformat(),
        "data_source": "MIMIC-IV Demo (Time-Shifted)",
        "metrics": {
            "icu_occupancy": {
                "current": icu_current,
                "status": get_status(icu_current, 90, 80),
                "unit": "%",
            },
            "er_arrivals": {
                "current": er_current,
                "status": get_status(er_current, 20, 15),
                "unit": "patients/hr",
            },
            "ward_occupancy": {
                "current": max(40, icu_current - 15),
                "status": get_status(max(40, icu_current - 15), 95, 85),
                "unit": "%",
            },
        }
    }


@router.get("/alerts", response_model=List[RiskEvent])
async def get_active_alerts():
    """
    Get currently active risk alerts based on forecast thresholds.
    """
    engine = get_replay_engine()
    alerts = []
    
    # Check ICU threshold
    icu = engine.get_icu_occupancy_forecast(hours=1)
    current_icu = icu.data_points[0].predicted_value if icu.data_points else 0
    
    if current_icu >= 85:
        alerts.append(RiskEvent(
            event_id=str(uuid.uuid4()),
            event_type="icu_capacity_critical" if current_icu >= 90 else "icu_capacity_warning",
            severity="critical" if current_icu >= 90 else "high",
            metric_name="icu_occupancy",
            current_value=current_icu,
            threshold_value=90 if current_icu >= 90 else 85,
            unit="%",
            affected_units=["Medical ICU", "Surgical ICU", "Cardiac ICU"],
        ))
    
    # Check ER surge
    er = engine.get_er_arrivals_forecast(hours=1)
    current_er = er.data_points[0].predicted_value if er.data_points else 0
    
    if current_er >= 15:
        alerts.append(RiskEvent(
            event_id=str(uuid.uuid4()),
            event_type="er_surge",
            severity="high" if current_er >= 20 else "medium",
            metric_name="er_arrivals",
            current_value=current_er,
            threshold_value=15,
            unit="patients/hr",
            affected_units=["Emergency Department"],
        ))
    
    return alerts
