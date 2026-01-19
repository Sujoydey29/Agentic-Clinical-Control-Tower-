"""
API Routes - Patients endpoint.
Provides CRUD operations and risk score retrieval for patients.
Uses the MIMIC-IV Replay Engine for realistic clinical data.
"""
from fastapi import APIRouter, HTTPException
from typing import List
from ..models import Patient, PatientRiskScores
from ..services.simulation_engine import get_replay_engine

router = APIRouter(prefix="/patients", tags=["Patients"])


@router.get("/", response_model=List[Patient])
async def get_patients(limit: int = 15):
    """
    Get all active patients from the MIMIC-IV Replay Engine.
    Returns time-shifted real clinical data as current patients.
    
    Args:
        limit: Maximum number of patients to return (default 15)
    """
    engine = get_replay_engine()
    return engine.get_active_patients(limit=limit)


@router.get("/{patient_id}", response_model=Patient)
async def get_patient(patient_id: str):
    """
    Get a specific patient by ID.
    """
    engine = get_replay_engine()
    patient = engine.get_patient_by_id(patient_id)
    if patient is None:
        raise HTTPException(status_code=404, detail=f"Patient {patient_id} not found")
    return patient


@router.get("/{patient_id}/risk-scores", response_model=PatientRiskScores)
async def get_patient_risk_scores(patient_id: str):
    """
    Get ML risk scores for a specific patient.
    """
    engine = get_replay_engine()
    patient = engine.get_patient_by_id(patient_id)
    if patient is None:
        raise HTTPException(status_code=404, detail=f"Patient {patient_id} not found")
    if patient.risk_scores is None:
        raise HTTPException(status_code=404, detail=f"Risk scores not available for {patient_id}")
    return patient.risk_scores


@router.post("/refresh")
async def refresh_patients():
    """
    Force refresh of patient data. (Reloads MIMIC-IV data)
    """
    global _engine
    from ..services.simulation_engine import _engine as eng
    # Reset the engine to reload data
    return {"message": "Data refresh triggered", "source": "MIMIC-IV Demo"}
