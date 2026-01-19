"""
API Routes - ML Predictions endpoint.
Provides clinical predictions using the ML models.
"""
from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List
from ..services.ml_models import get_risk_models
from ..services.feature_store import get_feature_store
from ..services.simulation_engine import get_replay_engine

router = APIRouter(prefix="/ml", tags=["Machine Learning"])


@router.get("/risk-scores/{patient_id}")
async def get_risk_scores(patient_id: str) -> Dict[str, Any]:
    """
    Get all ML-computed risk scores for a patient.
    
    Returns:
        - discharge_readiness: 0-100
        - readmission_risk_30d: 0-100
        - expected_los_days: float
        - escalation_risk_24h: 0-100
        - risk_level: critical/high/medium/low
    """
    # Extract subject_id from patient_id (e.g., "P-12345" -> 12345)
    try:
        subject_id = int(patient_id.replace("P-", ""))
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid patient ID format")
    
    models = get_risk_models()
    scores = models.get_all_risk_scores(subject_id)
    
    return scores


@router.get("/features/{patient_id}")
async def get_patient_features(patient_id: str) -> Dict[str, Any]:
    """
    Get extracted ML features for a patient.
    
    Useful for debugging and understanding model inputs.
    """
    try:
        subject_id = int(patient_id.replace("P-", ""))
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid patient ID format")
    
    store = get_feature_store()
    features = store.get_all_features(subject_id)
    
    return {
        "patient_id": patient_id,
        "features": features,
        "feature_buckets": {
            "demographics": store.extract_demographics(subject_id),
            "clinical": store.extract_clinical(subject_id),
            "operational": store.extract_operational(subject_id),
        }
    }


@router.get("/predictions/discharge-readiness/{patient_id}")
async def predict_discharge(patient_id: str) -> Dict[str, Any]:
    """Get discharge readiness prediction with explanation."""
    try:
        subject_id = int(patient_id.replace("P-", ""))
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid patient ID format")
    
    models = get_risk_models()
    score, details = models.predict_discharge_readiness(subject_id)
    
    return {
        "patient_id": patient_id,
        "prediction": "ready" if score >= 70 else ("borderline" if score >= 50 else "not_ready"),
        "probability": round(score, 1),
        "details": details,
    }


@router.get("/predictions/readmission-risk/{patient_id}")
async def predict_readmission(patient_id: str) -> Dict[str, Any]:
    """Get 30-day readmission risk prediction."""
    try:
        subject_id = int(patient_id.replace("P-", ""))
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid patient ID format")
    
    models = get_risk_models()
    score, details = models.predict_readmission_risk(subject_id)
    
    return {
        "patient_id": patient_id,
        "risk_level": "high" if score >= 60 else ("medium" if score >= 40 else "low"),
        "probability": round(score, 1),
        "details": details,
    }


@router.get("/predictions/batch")
async def batch_predictions(limit: int = 10) -> Dict[str, Any]:
    """
    Get risk predictions for all active patients.
    
    Useful for dashboard overview.
    """
    engine = get_replay_engine()
    models = get_risk_models()
    
    patients = engine.get_active_patients(limit=limit)
    predictions = []
    
    for patient in patients:
        patient_id = patient.demographics.patient_id
        try:
            subject_id = int(patient_id.replace("P-", ""))
            scores = models.get_all_risk_scores(subject_id)
            predictions.append({
                "patient_id": patient_id,
                "name": patient.demographics.name,
                "unit": patient.demographics.unit,
                "scores": scores["scores"],
                "risk_level": scores["risk_level"],
            })
        except Exception as e:
            continue
    
    # Sort by escalation risk (highest first)
    predictions.sort(key=lambda x: x["scores"]["escalation_risk_24h"], reverse=True)
    
    return {
        "count": len(predictions),
        "high_risk_count": len([p for p in predictions if p["risk_level"] in ["critical", "high"]]),
        "predictions": predictions,
    }


@router.get("/status")
async def ml_status() -> Dict[str, Any]:
    """Get ML engine status."""
    return {
        "status": "operational",
        "models": {
            "discharge_readiness": {"type": "LogisticRegression", "status": "active"},
            "readmission_risk": {"type": "GradientBoostingClassifier", "status": "active"},
            "los_prediction": {"type": "LinearRegression", "status": "active"},
            "escalation_risk": {"type": "RandomForestClassifier", "status": "active"},
        },
        "feature_store": "MIMIC-IV based",
        "data_source": "demo_dataset",
    }
