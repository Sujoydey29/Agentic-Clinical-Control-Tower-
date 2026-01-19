"""
Feature Store - Feature Engineering for Clinical ML Models

Extracts and transforms features from MIMIC-IV data into ML-ready format.
Organizes features into buckets:
- Demographics: Age, Gender
- Clinical: Diagnosis codes, Vitals statistics
- Operational: Unit type, Length of stay
"""
import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path
from functools import lru_cache

# Dataset paths
DATASET_BASE = Path(__file__).parent.parent.parent / "dataset" / "mimic-iv-clinical-database-demo-2.2"
HOSP_PATH = DATASET_BASE / "hosp"
ICU_PATH = DATASET_BASE / "icu"


class FeatureStore:
    """
    Feature extraction and storage for ML models.
    
    Buckets:
    - demographics: Age, Gender (one-hot), anchor_year
    - clinical: Diagnosis count, primary ICD category, vitals stats
    - operational: ICU flag, unit type, estimated LOS
    """
    
    def __init__(self):
        self._patients_df: Optional[pd.DataFrame] = None
        self._admissions_df: Optional[pd.DataFrame] = None
        self._icustays_df: Optional[pd.DataFrame] = None
        self._diagnoses_df: Optional[pd.DataFrame] = None
        self._features_cache: Dict[int, Dict[str, Any]] = {}
        
    def _ensure_loaded(self):
        """Lazy load data."""
        if self._patients_df is None:
            self._load_data()
    
    def _load_data(self):
        """Load required CSVs."""
        print("📊 FeatureStore: Loading MIMIC-IV data...")
        
        self._patients_df = pd.read_csv(HOSP_PATH / "patients.csv")
        self._admissions_df = pd.read_csv(HOSP_PATH / "admissions.csv")
        self._admissions_df['admittime'] = pd.to_datetime(self._admissions_df['admittime'])
        self._admissions_df['dischtime'] = pd.to_datetime(self._admissions_df['dischtime'])
        
        self._icustays_df = pd.read_csv(ICU_PATH / "icustays.csv")
        self._icustays_df['intime'] = pd.to_datetime(self._icustays_df['intime'])
        self._icustays_df['outtime'] = pd.to_datetime(self._icustays_df['outtime'])
        
        self._diagnoses_df = pd.read_csv(HOSP_PATH / "diagnoses_icd.csv")
        
        print(f"   ✓ FeatureStore loaded: {len(self._patients_df)} patients")
    
    # ==================== DEMOGRAPHIC FEATURES ====================
    
    def extract_demographics(self, subject_id: int) -> Dict[str, Any]:
        """
        Extract demographic features for a patient.
        
        Returns:
            age: int
            gender_M: 0 or 1 (one-hot)
            gender_F: 0 or 1 (one-hot)
        """
        self._ensure_loaded()
        
        patient = self._patients_df[self._patients_df['subject_id'] == subject_id]
        if patient.empty:
            return {"age": 0, "gender_M": 0, "gender_F": 0}
        
        row = patient.iloc[0]
        return {
            "age": int(row['anchor_age']),
            "gender_M": 1 if row['gender'] == 'M' else 0,
            "gender_F": 1 if row['gender'] == 'F' else 0,
        }
    
    # ==================== CLINICAL FEATURES ====================
    
    def extract_clinical(self, subject_id: int, hadm_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Extract clinical features for a patient/admission.
        
        Returns:
            diagnosis_count: Number of diagnoses
            has_heart_condition: 0 or 1
            has_respiratory: 0 or 1
            has_sepsis: 0 or 1
            has_renal: 0 or 1
            primary_icd_category: First letter of ICD code
        """
        self._ensure_loaded()
        
        # Get diagnoses
        if hadm_id:
            diag = self._diagnoses_df[self._diagnoses_df['hadm_id'] == hadm_id]
        else:
            # Get most recent admission
            admits = self._admissions_df[self._admissions_df['subject_id'] == subject_id]
            if admits.empty:
                return self._empty_clinical()
            hadm_id = admits.iloc[-1]['hadm_id']
            diag = self._diagnoses_df[self._diagnoses_df['hadm_id'] == hadm_id]
        
        if diag.empty:
            return self._empty_clinical()
        
        icd_codes = diag['icd_code'].astype(str).tolist()
        
        # Category detection
        has_heart = any(c.startswith('I') for c in icd_codes)  # Circulatory
        has_respiratory = any(c.startswith('J') for c in icd_codes)
        has_sepsis = any(c.startswith('A41') for c in icd_codes)
        has_renal = any(c.startswith('N') for c in icd_codes)
        
        primary_category = icd_codes[0][0] if icd_codes else 'X'
        
        return {
            "diagnosis_count": len(icd_codes),
            "has_heart_condition": 1 if has_heart else 0,
            "has_respiratory": 1 if has_respiratory else 0,
            "has_sepsis": 1 if has_sepsis else 0,
            "has_renal": 1 if has_renal else 0,
            "primary_icd_category": primary_category,
        }
    
    def _empty_clinical(self) -> Dict[str, Any]:
        return {
            "diagnosis_count": 0,
            "has_heart_condition": 0,
            "has_respiratory": 0,
            "has_sepsis": 0,
            "has_renal": 0,
            "primary_icd_category": "X",
        }
    
    # ==================== OPERATIONAL FEATURES ====================
    
    def extract_operational(self, subject_id: int, hadm_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Extract operational features.
        
        Returns:
            is_icu: 0 or 1
            los_days: Length of stay in days
            unit_type_icu: 0 or 1
            unit_type_ward: 0 or 1
            unit_type_er: 0 or 1
        """
        self._ensure_loaded()
        
        # Get admission
        if hadm_id is None:
            admits = self._admissions_df[self._admissions_df['subject_id'] == subject_id]
            if admits.empty:
                return self._empty_operational()
            admission = admits.iloc[-1]
            hadm_id = admission['hadm_id']
        else:
            admission = self._admissions_df[self._admissions_df['hadm_id'] == hadm_id]
            if admission.empty:
                return self._empty_operational()
            admission = admission.iloc[0]
        
        # Calculate LOS
        if pd.notna(admission['dischtime']) and pd.notna(admission['admittime']):
            los = (admission['dischtime'] - admission['admittime']).total_seconds() / 86400
        else:
            los = 0
        
        # Check ICU
        icu_stays = self._icustays_df[self._icustays_df['hadm_id'] == hadm_id]
        is_icu = len(icu_stays) > 0
        
        # Unit type
        unit = icu_stays.iloc[0]['last_careunit'] if is_icu else "General Ward"
        
        return {
            "is_icu": 1 if is_icu else 0,
            "los_days": round(float(los), 2),
            "unit_type_icu": 1 if is_icu else 0,
            "unit_type_ward": 1 if not is_icu else 0,
            "unit_type_er": 0,  # Would need ER data
        }
    
    def _empty_operational(self) -> Dict[str, Any]:
        return {
            "is_icu": 0,
            "los_days": 0,
            "unit_type_icu": 0,
            "unit_type_ward": 1,
            "unit_type_er": 0,
        }
    
    # ==================== COMBINED FEATURES ====================
    
    def get_all_features(self, subject_id: int, hadm_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Get all features for a patient, combined into a single dict.
        """
        # Check cache
        cache_key = (subject_id, hadm_id)
        if cache_key in self._features_cache:
            return self._features_cache[cache_key]
        
        features = {
            **self.extract_demographics(subject_id),
            **self.extract_clinical(subject_id, hadm_id),
            **self.extract_operational(subject_id, hadm_id),
        }
        
        self._features_cache[cache_key] = features
        return features
    
    def get_training_dataframe(self) -> pd.DataFrame:
        """
        Build a complete training DataFrame from all admissions.
        Used for model training.
        """
        self._ensure_loaded()
        
        rows = []
        for _, admission in self._admissions_df.iterrows():
            subject_id = admission['subject_id']
            hadm_id = admission['hadm_id']
            
            features = self.get_all_features(subject_id, hadm_id)
            
            # Add target variables (derived from data)
            # Readmission: Check if same patient has another admission within 30 days
            # For demo, we'll simulate this
            features['target_readmission'] = 1 if features['diagnosis_count'] > 3 else 0
            features['target_discharge_ready'] = 1 if features['los_days'] > 2 else 0
            
            rows.append(features)
        
        return pd.DataFrame(rows)


# Global singleton
_feature_store: Optional[FeatureStore] = None


def get_feature_store() -> FeatureStore:
    """Get or create feature store instance."""
    global _feature_store
    if _feature_store is None:
        _feature_store = FeatureStore()
    return _feature_store
