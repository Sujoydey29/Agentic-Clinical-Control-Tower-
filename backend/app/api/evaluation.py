"""
API Routes - Evaluation & Safety.
Exposes endpoints for feedback, metrics, and audit trails.
"""
from fastapi import APIRouter, HTTPException, Body
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from datetime import datetime

from ..services.evaluation import get_eval_service

router = APIRouter(prefix="/evaluation", tags=["Evaluation & Safety"])


class FeedbackRequest(BaseModel):
    """User feedback submission."""
    workflow_id: str
    feedback_type: str  # thumbs_up, thumbs_down, edited
    comments: Optional[str] = None
    user_role: str = "unknown"


@router.post("/feedback")
async def submit_feedback(request: FeedbackRequest) -> Dict[str, Any]:
    """Submit human feedback for a workflow."""
    service = get_eval_service()
    service.submit_feedback(
        request.workflow_id, 
        request.feedback_type, 
        request.comments, 
        request.user_role
    )
    return {"status": "recorded", "timestamp": datetime.utcnow()}


@router.get("/metrics")
async def get_system_metrics() -> Dict[str, Any]:
    """Get current system performance metrics."""
    service = get_eval_service()
    return service.get_metrics_summary()


@router.get("/audit/{workflow_id}")
async def get_audit_trail(workflow_id: str) -> Dict[str, Any]:
    """Retrieve full audit trail for a specific workflow."""
    service = get_eval_service()
    trail = service.get_audit_trail(workflow_id)
    
    if "error" in trail:
        raise HTTPException(status_code=404, detail=trail["error"])
        
    return trail
