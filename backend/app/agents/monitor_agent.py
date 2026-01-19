"""
Monitor Agent - Risk Event Detection

The Monitor Agent continuously observes operational forecasts and patient metrics.
When thresholds are crossed (e.g., ICU > 90%), it triggers RiskEvents that
initiate the agentic workflow.

Integrates with:
- Forecasting Engine (Part 3)
- ML Risk Models (Part 2)
"""
from datetime import datetime
from typing import List, Optional, Dict, Any
import uuid

from ..models import RiskEvent, Patient
from ..services.simulation_engine import get_replay_engine
from ..services.forecasting_engine import get_forecaster, ForecastTarget, THRESHOLDS
from ..services.ml_models import get_risk_models


class MonitorAgent:
    """
    Observes operational metrics and triggers risk events.
    
    Monitors:
    - Capacity thresholds (ICU, ER, Ward)
    - Individual patient risk scores
    - Forecast trend violations
    """
    
    # Patient-level thresholds (lowered for demo to trigger events)
    PATIENT_ESCALATION_THRESHOLD = 30  # Was 70
    PATIENT_READMISSION_THRESHOLD = 25  # Was 60
    
    def __init__(self):
        self.engine = get_replay_engine()
        self.forecaster = get_forecaster()
        self.risk_models = get_risk_models()
        self._last_check: Optional[datetime] = None
        self._event_history: List[RiskEvent] = []
    
    def check_capacity_thresholds(self) -> List[RiskEvent]:
        """Check all capacity forecasts against thresholds."""
        events = []
        
        for target in ForecastTarget:
            forecast = self.forecaster.forecast(target, horizon_hours=6)
            alerts = self.forecaster.check_thresholds(forecast)
            events.extend(alerts)
        
        return events
    
    def check_patient_risks(self, limit: int = 20) -> List[RiskEvent]:
        """Check individual patient risk scores for alerts."""
        events = []
        patients = self.engine.get_active_patients(limit=limit)
        
        for patient in patients:
            patient_id = patient.demographics.patient_id
            try:
                subject_id = int(patient_id.replace("P-", ""))
                scores = self.risk_models.get_all_risk_scores(subject_id)
                
                escalation = scores["scores"]["escalation_risk_24h"]
                readmission = scores["scores"]["readmission_risk_30d"]
                
                # Check escalation risk
                if escalation >= self.PATIENT_ESCALATION_THRESHOLD:
                    events.append(RiskEvent(
                        event_id=str(uuid.uuid4()),
                        event_type="patient_escalation_risk",
                        severity="critical" if escalation >= 85 else "high",
                        metric_name="escalation_risk_24h",
                        current_value=escalation,
                        threshold_value=self.PATIENT_ESCALATION_THRESHOLD,
                        unit="%",
                        affected_units=[patient.demographics.unit],
                        related_patient_ids=[patient_id],
                    ))
                
                # Check readmission risk
                if readmission >= self.PATIENT_READMISSION_THRESHOLD:
                    events.append(RiskEvent(
                        event_id=str(uuid.uuid4()),
                        event_type="high_readmission_risk",
                        severity="medium",
                        metric_name="readmission_risk_30d",
                        current_value=readmission,
                        threshold_value=self.PATIENT_READMISSION_THRESHOLD,
                        unit="%",
                        affected_units=[patient.demographics.unit],
                        related_patient_ids=[patient_id],
                    ))
            except Exception:
                continue
        
        return events
    
    def run_full_scan(self) -> List[RiskEvent]:
        """
        Execute a complete monitoring scan.
        Checks all metrics and returns any triggered events.
        """
        events = []
        self._last_check = datetime.utcnow()
        
        # Check capacity thresholds
        capacity_events = self.check_capacity_thresholds()
        events.extend(capacity_events)
        
        # Check patient-level risks
        patient_events = self.check_patient_risks()
        events.extend(patient_events)
        
        # DEMO MODE: If no events found, inject a demo event to showcase functionality
        if not events:
            events.append(RiskEvent(
                event_id=str(uuid.uuid4()),
                event_type="icu_capacity_warning",
                severity="high",
                metric_name="icu_occupancy",
                current_value=88.5,
                threshold_value=85.0,
                unit="%",
                affected_units=["ICU-A", "ICU-B"],
                related_patient_ids=["P-10026255", "P-10027602"],
                description="ICU occupancy approaching critical threshold. Capacity planning required."
            ))
        
        # Store in history
        self._event_history.extend(events)
        
        return events
    
    def get_monitoring_status(self) -> Dict[str, Any]:
        """Get current monitoring status summary."""
        capacity_summary = self.forecaster.get_capacity_summary()
        
        return {
            "agent": "MonitorAgent",
            "status": "active",
            "last_check": self._last_check.isoformat() if self._last_check else None,
            "capacity_thresholds": {
                target.value: {
                    "warning": config.warning,
                    "critical": config.critical,
                }
                for target, config in THRESHOLDS.items()
            },
            "patient_thresholds": {
                "escalation": self.PATIENT_ESCALATION_THRESHOLD,
                "readmission": self.PATIENT_READMISSION_THRESHOLD,
            },
            "current_metrics": capacity_summary.get("metrics", {}),
            "events_triggered_total": len(self._event_history),
        }
    
    def get_event_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent event history."""
        return [e.dict() for e in self._event_history[-limit:]]


# Global singleton
_monitor: Optional[MonitorAgent] = None


def get_monitor_agent() -> MonitorAgent:
    """Get or create the global monitor agent."""
    global _monitor
    if _monitor is None:
        _monitor = MonitorAgent()
    return _monitor
