"""
API Routes - Communication endpoint.
Provies GenAI message generation and reporting.
"""
from fastapi import APIRouter, HTTPException, Body
from pydantic import BaseModel
from typing import Dict, Any, List, Optional

from ..services.genai_communication import get_comm_service, TargetRole
from ..models import ActionCard, RiskEvent

router = APIRouter(prefix="/communication", tags=["GenAI Communication"])


class MessageRequest(BaseModel):
    """Request to generate a message."""
    action_card: ActionCard
    role: TargetRole
    risk_event: Optional[RiskEvent] = None


class ReportRequest(BaseModel):
    """Request for a shift report."""
    hours: int = 12
    events: List[Dict[str, Any]]


class SimulationRequest(BaseModel):
    """Request for scenario simulation."""
    scenario: str


@router.post("/generate-message")
async def generate_message(request: MessageRequest) -> Dict[str, Any]:
    """
    Generate a tailored message for a specific role based on an ActionCard.
    Roles: physician, nurse, admin, patient
    """
    service = get_comm_service()
    message = await service.generate_message(request.action_card, request.role, request.risk_event)
    
    return {
        "role": request.role,
        "message": message,
        "generated_at": request.action_card.generated_at
    }


@router.post("/shift-report")
async def generate_shift_report(request: ReportRequest) -> Dict[str, Any]:
    """
    Generate a shift handoff report from a list of events.
    """
    service = get_comm_service()
    report = await service.generate_shift_report(request.events, request.hours)
    
    return {
        "report": report,
        "time_range_hours": request.hours,
        "event_count": len(request.events)
    }


@router.post("/simulate")
async def run_simulation(request: SimulationRequest) -> Dict[str, Any]:
    """
    Run a 'What-If' scenario simulation.
    """
    service = get_comm_service()
    result = await service.simulate_scenario(request.scenario)
    
    return {
        "scenario": request.scenario,
        "simulation_result": result
    }
