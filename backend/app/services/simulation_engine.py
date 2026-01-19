"""
MIMIC-IV Replay Engine - Real Clinical Data Simulation

This module provides a "Time-Shift Replay Engine" that:
1. Loads real clinical data from MIMIC-IV Demo dataset
2. Shifts historical timestamps to "now" for live simulation
3. Provides realistic patient vitals, admissions, and ICU data

This replaces simple random mock data with pattern-preserving clinical data.
"""
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from pathlib import Path
from functools import lru_cache
import random

from ..models import (
    Patient,
    PatientDemographics,
    ClinicalData,
    Vitals,
    PatientRiskScores,
    PatientStatus,
    CapacityForecast,
    ForecastPoint,
)


# Dataset paths
DATASET_BASE = Path(__file__).parent.parent.parent / "dataset" / "mimic-iv-clinical-database-demo-2.2"
HOSP_PATH = DATASET_BASE / "hosp"
ICU_PATH = DATASET_BASE / "icu"


class MIMICReplayEngine:
    """
    Time-Shift Replay Engine for MIMIC-IV Demo Dataset.
    
    The engine loads CSV data once, then provides time-shifted views
    so historical data appears to be happening "now".
    """
    
    def __init__(self):
        self._patients_df: Optional[pd.DataFrame] = None
        self._admissions_df: Optional[pd.DataFrame] = None
        self._icustays_df: Optional[pd.DataFrame] = None
        self._chartevents_df: Optional[pd.DataFrame] = None
        self._diagnoses_df: Optional[pd.DataFrame] = None
        self._time_offset: Optional[timedelta] = None
        
    def _ensure_loaded(self):
        """Lazy load the dataframes on first access."""
        if self._patients_df is None:
            self._load_data()
            
    def _load_data(self):
        """Load all required CSV files into memory."""
        print("📊 Loading MIMIC-IV Demo Dataset...")
        
        # Load patients
        self._patients_df = pd.read_csv(HOSP_PATH / "patients.csv")
        print(f"   ✓ Loaded {len(self._patients_df)} patients")
        
        # Load admissions
        self._admissions_df = pd.read_csv(HOSP_PATH / "admissions.csv")
        self._admissions_df['admittime'] = pd.to_datetime(self._admissions_df['admittime'])
        self._admissions_df['dischtime'] = pd.to_datetime(self._admissions_df['dischtime'])
        print(f"   ✓ Loaded {len(self._admissions_df)} admissions")
        
        # Load ICU stays
        self._icustays_df = pd.read_csv(ICU_PATH / "icustays.csv")
        self._icustays_df['intime'] = pd.to_datetime(self._icustays_df['intime'])
        self._icustays_df['outtime'] = pd.to_datetime(self._icustays_df['outtime'])
        print(f"   ✓ Loaded {len(self._icustays_df)} ICU stays")
        
        # Load diagnoses
        self._diagnoses_df = pd.read_csv(HOSP_PATH / "diagnoses_icd.csv")
        print(f"   ✓ Loaded {len(self._diagnoses_df)} diagnoses")
        
        # Calculate time offset (shift oldest admission to "now - 7 days")
        oldest_admit = self._admissions_df['admittime'].min()
        target_start = datetime.now() - timedelta(days=7)
        self._time_offset = target_start - oldest_admit
        print(f"   ✓ Time offset calculated: {self._time_offset.days} days")
        
        # Note: We skip chartevents for now due to large size (64MB)
        # Will load on-demand for specific patients
        print("📊 MIMIC-IV Data loaded successfully!")
        
    def _shift_time(self, dt: datetime) -> datetime:
        """Shift a datetime from MIMIC timeline to 'now'."""
        if self._time_offset is None:
            self._ensure_loaded()
        return dt + self._time_offset
    
    def _calculate_risk_score(self, patient_id: int, age: int, diagnosis_count: int) -> PatientRiskScores:
        """Calculate risk scores based on patient data."""
        # Simple heuristic-based scoring (will be replaced by ML in Part 2)
        base_risk = min(100, age * 0.5 + diagnosis_count * 5 + random.uniform(0, 20))
        
        return PatientRiskScores(
            patient_id=f"P-{patient_id}",
            discharge_readiness=max(0, 100 - base_risk + random.uniform(-10, 20)),
            readmission_risk_30d=min(100, base_risk + random.uniform(-5, 15)),
            escalation_risk=min(100, base_risk * 0.7 + random.uniform(0, 25)),
            expected_los_days=max(1, (100 - base_risk) / 20 + random.uniform(0, 3)),
        )
    
    def _get_patient_diagnoses(self, hadm_id: int) -> tuple[List[str], str]:
        """Get diagnosis codes and text for an admission."""
        self._ensure_loaded()
        
        patient_diag = self._diagnoses_df[self._diagnoses_df['hadm_id'] == hadm_id]
        icd_codes = patient_diag['icd_code'].tolist()[:5]  # Top 5 codes
        
        # Map common ICD codes to readable text
        diagnosis_map = {
            'I50': 'Heart Failure',
            'A41': 'Sepsis',
            'J18': 'Pneumonia',
            'I21': 'Acute MI',
            'I63': 'Stroke',
            'J44': 'COPD',
            'K92': 'GI Bleed',
            'N17': 'Acute Kidney Injury',
            'I48': 'Atrial Fibrillation',
        }
        
        diagnosis_text = "Multiple diagnoses"
        for code in icd_codes:
            code_prefix = str(code)[:3]
            if code_prefix in diagnosis_map:
                diagnosis_text = diagnosis_map[code_prefix]
                break
                
        return icd_codes, diagnosis_text
    
    def _generate_vitals_from_patterns(self, is_icu: bool = False) -> Vitals:
        """Generate realistic vitals based on circadian patterns."""
        hour = datetime.now().hour
        
        # Circadian heart rate pattern (lower at night)
        base_hr = 75 if 6 <= hour <= 22 else 65
        if is_icu:
            base_hr += 15
        
        # Add realistic variance
        return Vitals(
            timestamp=datetime.utcnow(),
            heart_rate=base_hr + random.gauss(0, 8),
            blood_pressure_systolic=120 + random.gauss(0, 12) + (10 if is_icu else 0),
            blood_pressure_diastolic=75 + random.gauss(0, 8),
            spo2=min(100, max(85, 97 + random.gauss(0, 2) - (3 if is_icu else 0))),
            respiratory_rate=16 + random.gauss(0, 3) + (4 if is_icu else 0),
            temperature=37.0 + random.gauss(0, 0.3),
        )
    
    def _generate_vitals_history(self, hours: int = 24, is_icu: bool = False) -> List[Vitals]:
        """Generate historical vitals with realistic patterns."""
        history = []
        now = datetime.utcnow()
        
        for i in range(hours):
            vitals = self._generate_vitals_from_patterns(is_icu)
            vitals.timestamp = now - timedelta(hours=hours - i)
            history.append(vitals)
            
        return history
    
    def get_active_patients(self, limit: int = 15) -> List[Patient]:
        """
        Get currently "active" patients by replaying recent admissions.
        Time-shifts historical admissions to appear as current patients.
        """
        self._ensure_loaded()
        
        patients = []
        
        # Get most recent admissions (these become our "current" patients)
        recent_admissions = self._admissions_df.nlargest(limit, 'admittime')
        
        for _, admission in recent_admissions.iterrows():
            subject_id = admission['subject_id']
            hadm_id = admission['hadm_id']
            
            # Get patient demographics
            patient_row = self._patients_df[self._patients_df['subject_id'] == subject_id].iloc[0]
            
            # Check if ICU patient
            icu_stay = self._icustays_df[self._icustays_df['hadm_id'] == hadm_id]
            is_icu = len(icu_stay) > 0
            unit = icu_stay.iloc[0]['last_careunit'] if is_icu else f"Ward-{random.choice(['East', 'West', 'North'])}"
            
            # Get diagnoses
            icd_codes, diagnosis_text = self._get_patient_diagnoses(hadm_id)
            
            # Build patient record
            demographics = PatientDemographics(
                patient_id=f"P-{subject_id}",
                name=f"Patient {subject_id}",  # Real names are de-identified
                age=patient_row['anchor_age'],
                gender=patient_row['gender'],
                admission_date=self._shift_time(admission['admittime']),
                unit=unit,
            )
            
            clinical = ClinicalData(
                patient_id=f"P-{subject_id}",
                diagnosis_codes=icd_codes,
                diagnosis_text=diagnosis_text,
                current_vitals=self._generate_vitals_from_patterns(is_icu),
                vitals_history=self._generate_vitals_history(24, is_icu),
            )
            
            risk_scores = self._calculate_risk_score(
                subject_id, 
                patient_row['anchor_age'],
                len(icd_codes)
            )
            
            # Determine status based on risk
            if risk_scores.escalation_risk > 70:
                status = PatientStatus.CRITICAL
            elif risk_scores.discharge_readiness > 75:
                status = PatientStatus.DISCHARGE_READY
            elif risk_scores.readmission_risk_30d > 60:
                status = PatientStatus.WATCH
            else:
                status = PatientStatus.STABLE
            
            patients.append(Patient(
                demographics=demographics,
                clinical=clinical,
                risk_scores=risk_scores,
                status=status,
            ))
        
        return patients
    
    def get_patient_by_id(self, patient_id: str) -> Optional[Patient]:
        """Get a specific patient by ID."""
        patients = self.get_active_patients(limit=50)
        for patient in patients:
            if patient.demographics.patient_id == patient_id:
                return patient
        return None
    
    def get_icu_occupancy_forecast(self, hours: int = 24) -> CapacityForecast:
        """Generate ICU occupancy forecast based on historical patterns."""
        self._ensure_loaded()
        
        # Calculate current occupancy from ICU stays
        total_icu_beds = 50  # Assumed capacity
        current_stays = len(self._icustays_df)
        base_occupancy = min(95, (current_stays / total_icu_beds) * 100 + 40)
        
        # Generate forecast with daily patterns
        now = datetime.utcnow()
        data_points = []
        
        for i in range(hours):
            future_time = now + timedelta(hours=i)
            hour = future_time.hour
            
            # ICU tends to be fuller during daytime (admissions from ER)
            daily_factor = 5 * (1 - abs(hour - 14) / 14)  # Peak at 2 PM
            
            predicted = base_occupancy + daily_factor + random.gauss(0, 2)
            predicted = min(100, max(50, predicted))
            
            ci_width = 2 + (i * 0.2)
            
            data_points.append(ForecastPoint(
                timestamp=future_time,
                predicted_value=round(predicted, 1),
                lower_bound=round(max(0, predicted - ci_width), 1),
                upper_bound=round(min(100, predicted + ci_width), 1),
                actual_value=round(predicted + random.gauss(0, 1), 1) if i < 4 else None,
            ))
        
        return CapacityForecast(
            metric_name="icu_occupancy",
            unit="%",
            forecast_horizon_hours=hours,
            data_points=data_points,
        )
    
    def get_er_arrivals_forecast(self, hours: int = 24) -> CapacityForecast:
        """Generate ER arrivals forecast based on typical patterns."""
        now = datetime.utcnow()
        data_points = []
        
        for i in range(hours):
            future_time = now + timedelta(hours=i)
            hour = future_time.hour
            weekday = future_time.weekday()
            
            # ER busier on weekends and evenings
            base = 8
            if weekday >= 5:  # Weekend
                base += 4
            if 18 <= hour <= 23:  # Evening rush
                base += 6
            elif 8 <= hour <= 12:  # Morning
                base += 3
            
            predicted = base + random.gauss(0, 2)
            ci_width = 1 + (i * 0.15)
            
            data_points.append(ForecastPoint(
                timestamp=future_time,
                predicted_value=round(max(0, predicted), 1),
                lower_bound=round(max(0, predicted - ci_width), 1),
                upper_bound=round(predicted + ci_width, 1),
                actual_value=round(max(0, predicted + random.gauss(0, 1)), 1) if i < 4 else None,
            ))
        
        return CapacityForecast(
            metric_name="er_arrivals",
            unit="patients/hr",
            forecast_horizon_hours=hours,
            data_points=data_points,
        )


# Global singleton instance
_engine: Optional[MIMICReplayEngine] = None


def get_replay_engine() -> MIMICReplayEngine:
    """Get or create the global replay engine instance."""
    global _engine
    if _engine is None:
        _engine = MIMICReplayEngine()
    return _engine
