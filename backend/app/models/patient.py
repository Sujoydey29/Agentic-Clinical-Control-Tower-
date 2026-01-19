"""
Pydantic models for data validation and serialization.
Represents the Feature Store data structures.
"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List
from enum import Enum


class PatientStatus(str, Enum):
    """Patient status enumeration."""
    CRITICAL = "Critical"
    STABLE = "Stable"
    WATCH = "Watch"
    DISCHARGE_READY = "Discharge Ready"


class RiskLevel(str, Enum):
    """Risk level classification."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


# ============= Demographics =============
class PatientDemographics(BaseModel):
    """Demographic information for a patient."""
    patient_id: str = Field(..., description="Unique patient identifier")
    name: str
    age: int = Field(..., ge=0, le=150)
    gender: str
    admission_date: datetime
    unit: str = Field(..., description="Hospital unit (e.g., ICU-A, Ward-East)")


# ============= Clinical Data =============
class Vitals(BaseModel):
    """Patient vital signs snapshot."""
    timestamp: datetime
    heart_rate: float = Field(..., ge=0, le=300, description="BPM")
    blood_pressure_systolic: float = Field(..., ge=0, le=300)
    blood_pressure_diastolic: float = Field(..., ge=0, le=200)
    spo2: float = Field(..., ge=0, le=100, description="Oxygen saturation %")
    respiratory_rate: float = Field(..., ge=0, le=60, description="Breaths per minute")
    temperature: float = Field(..., ge=30, le=45, description="Celsius")


class ClinicalData(BaseModel):
    """Clinical information for a patient."""
    patient_id: str
    diagnosis_codes: List[str] = Field(default_factory=list, description="ICD-10 codes")
    diagnosis_text: str
    current_vitals: Optional[Vitals] = None
    vitals_history: List[Vitals] = Field(default_factory=list)


# ============= Operational Data =============
class BedInfo(BaseModel):
    """Bed and unit information."""
    bed_id: str
    unit: str
    bed_type: str = Field(..., description="ICU, Ward, ER, etc.")
    is_occupied: bool = True
    patient_id: Optional[str] = None


class StaffInfo(BaseModel):
    """Staff on duty information."""
    staff_id: str
    name: str
    role: str
    unit: str
    shift_start: datetime
    shift_end: datetime


# ============= ML Scores =============
class PatientRiskScores(BaseModel):
    """ML-generated risk scores for a patient."""
    patient_id: str
    discharge_readiness: float = Field(..., ge=0, le=100, description="Probability of safe discharge")
    readmission_risk_30d: float = Field(..., ge=0, le=100, description="30-day readmission risk")
    escalation_risk: float = Field(..., ge=0, le=100, description="Risk of critical event in next 24h")
    expected_los_days: float = Field(..., ge=0, description="Expected Length of Stay")
    calculated_at: datetime = Field(default_factory=datetime.utcnow)


# ============= Forecast Data =============
class ForecastPoint(BaseModel):
    """Single forecast data point with confidence intervals."""
    timestamp: datetime
    predicted_value: float
    lower_bound: float
    upper_bound: float
    actual_value: Optional[float] = None


class CapacityForecast(BaseModel):
    """Time-series forecast for capacity metrics."""
    metric_name: str = Field(..., description="e.g., 'icu_occupancy', 'er_arrivals'")
    unit: Optional[str] = None
    forecast_horizon_hours: int = 24
    data_points: List[ForecastPoint] = Field(default_factory=list)
    generated_at: datetime = Field(default_factory=datetime.utcnow)


# ============= Complete Patient Record =============
class Patient(BaseModel):
    """Complete patient record combining all data sources."""
    demographics: PatientDemographics
    clinical: ClinicalData
    risk_scores: Optional[PatientRiskScores] = None
    status: PatientStatus = PatientStatus.STABLE

    class Config:
        from_attributes = True
