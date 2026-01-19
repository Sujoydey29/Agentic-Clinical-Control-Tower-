"""
Mock Data Service - Generates realistic healthcare data for development.
This will be replaced with real database queries in production.
"""
import random
from datetime import datetime, timedelta
from typing import List
from ..models import (
    Patient,
    PatientDemographics,
    ClinicalData,
    Vitals,
    PatientRiskScores,
    PatientStatus,
    BedInfo,
    StaffInfo,
    CapacityForecast,
    ForecastPoint,
)


# Sample data pools
FIRST_NAMES = ["Sarah", "Logan", "Jean", "Wade", "Tony", "Pepper", "Bruce", "Natasha", "Steve", "Wanda"]
LAST_NAMES = ["Connor", "Grey", "Wilson", "Stark", "Banner", "Rogers", "Maximoff", "Rhodes", "Barnes", "Lang"]
DIAGNOSES = [
    ("Heart Failure", ["I50.9", "I11.9"]),
    ("Sepsis", ["A41.9", "R65.20"]),
    ("Pneumonia", ["J18.9", "J15.9"]),
    ("Acute MI", ["I21.9", "I25.10"]),
    ("Stroke", ["I63.9", "G45.9"]),
    ("COPD Exacerbation", ["J44.1", "J96.00"]),
    ("GI Bleed", ["K92.2", "K25.4"]),
    ("Trauma", ["S00-T88", "V00-Y99"]),
    ("Arrhythmia", ["I49.9", "I48.91"]),
    ("Renal Failure", ["N17.9", "N18.6"]),
]
UNITS = ["ICU-A", "ICU-B", "ICU-C", "Ward-East", "Ward-West", "ER-Trauma", "ER-General", "Cardiac-ICU"]


def generate_vitals(is_critical: bool = False) -> Vitals:
    """Generate realistic vital signs."""
    base_hr = 100 if is_critical else 75
    base_spo2 = 88 if is_critical else 97
    
    return Vitals(
        timestamp=datetime.utcnow(),
        heart_rate=base_hr + random.uniform(-15, 25),
        blood_pressure_systolic=random.uniform(100 if is_critical else 110, 160 if is_critical else 135),
        blood_pressure_diastolic=random.uniform(60, 95),
        spo2=min(100, max(70, base_spo2 + random.uniform(-5, 3))),
        respiratory_rate=random.uniform(14 if not is_critical else 22, 22 if not is_critical else 32),
        temperature=random.uniform(36.5, 38.5 if is_critical else 37.2),
    )


def generate_vitals_history(hours: int = 24, is_critical: bool = False) -> List[Vitals]:
    """Generate historical vital signs."""
    history = []
    now = datetime.utcnow()
    for i in range(hours):
        vitals = generate_vitals(is_critical)
        vitals.timestamp = now - timedelta(hours=hours - i)
        history.append(vitals)
    return history


def generate_patient(patient_id: str) -> Patient:
    """Generate a complete mock patient record."""
    diagnosis, icd_codes = random.choice(DIAGNOSES)
    is_critical = diagnosis in ["Sepsis", "Acute MI", "Stroke"]
    
    # Risk scores correlate with diagnosis severity
    base_risk = 80 if is_critical else random.uniform(20, 60)
    
    demographics = PatientDemographics(
        patient_id=patient_id,
        name=f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}",
        age=random.randint(25, 85),
        gender=random.choice(["Male", "Female"]),
        admission_date=datetime.utcnow() - timedelta(days=random.randint(0, 14)),
        unit=random.choice(UNITS[:4]) if is_critical else random.choice(UNITS[4:]),
    )
    
    clinical = ClinicalData(
        patient_id=patient_id,
        diagnosis_codes=icd_codes,
        diagnosis_text=diagnosis,
        current_vitals=generate_vitals(is_critical),
        vitals_history=generate_vitals_history(24, is_critical),
    )
    
    risk_scores = PatientRiskScores(
        patient_id=patient_id,
        discharge_readiness=max(0, 100 - base_risk + random.uniform(-10, 10)),
        readmission_risk_30d=min(100, base_risk + random.uniform(-5, 15)),
        escalation_risk=min(100, base_risk + random.uniform(-10, 20)) if is_critical else random.uniform(5, 25),
        expected_los_days=random.uniform(2, 14) if is_critical else random.uniform(1, 5),
    )
    
    status = PatientStatus.CRITICAL if is_critical else (
        PatientStatus.DISCHARGE_READY if risk_scores.discharge_readiness > 70 else PatientStatus.STABLE
    )
    
    return Patient(
        demographics=demographics,
        clinical=clinical,
        risk_scores=risk_scores,
        status=status,
    )


def generate_patients(count: int = 10) -> List[Patient]:
    """Generate a list of mock patients."""
    return [generate_patient(f"P-{100 + i}") for i in range(count)]


def generate_forecast(metric_name: str, hours: int = 24, base_value: float = 75) -> CapacityForecast:
    """Generate a mock capacity forecast with confidence intervals."""
    now = datetime.utcnow()
    data_points = []
    
    current = base_value
    for i in range(hours):
        # Add some trend and noise
        trend = 0.5 * (i / hours)  # Slight upward trend
        noise = random.uniform(-3, 3)
        current = max(0, min(100, current + trend + noise))
        
        # Confidence interval widens as we go further into the future
        ci_width = 2 + (i * 0.3)
        
        data_points.append(ForecastPoint(
            timestamp=now + timedelta(hours=i),
            predicted_value=round(current, 1),
            lower_bound=round(max(0, current - ci_width), 1),
            upper_bound=round(min(100, current + ci_width), 1),
            actual_value=round(current + random.uniform(-2, 2), 1) if i < 6 else None,  # Only recent actuals
        ))
    
    return CapacityForecast(
        metric_name=metric_name,
        forecast_horizon_hours=hours,
        data_points=data_points,
    )


def generate_bed_status() -> List[BedInfo]:
    """Generate mock bed occupancy data."""
    beds = []
    for unit in UNITS:
        bed_count = 8 if "ICU" in unit else 20
        for i in range(bed_count):
            beds.append(BedInfo(
                bed_id=f"{unit}-B{i+1:02d}",
                unit=unit,
                bed_type="ICU" if "ICU" in unit else ("ER" if "ER" in unit else "Ward"),
                is_occupied=random.random() < 0.85,  # 85% occupancy
                patient_id=f"P-{random.randint(100, 200)}" if random.random() < 0.85 else None,
            ))
    return beds
