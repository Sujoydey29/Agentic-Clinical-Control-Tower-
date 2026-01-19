"""
API Routes - Agents endpoint.
Provides agentic workflow execution and management.
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional

from ..agents.orchestrator import get_orchestrator, WorkflowStatus

router = APIRouter(prefix="/agents", tags=["Agentic Orchestration"])


class WorkflowTrigger(BaseModel):
    """Input for triggering a workflow."""
    trigger_type: str = "auto"  # auto, manual
    target_role: str = "nurse"  # physician, nurse, admin


class ActionApproval(BaseModel):
    """Input for approving/rejecting actions."""
    approved: bool
    reason: Optional[str] = None


@router.post("/run")
async def run_agent_workflow(trigger: WorkflowTrigger) -> Dict[str, Any]:
    """
    Run the complete agent workflow.
    
    Workflow:
    1. Monitor Agent - Detects risk events
    2. Retrieval Agent - Fetches relevant SOPs
    3. Planning Agent - LLM generates ActionCard
    4. Guardrail Agent - Validates the plan
    5. Notifier Agent - Formats for target role
    
    Returns workflow state with ActionCard if successful.
    """
    orchestrator = get_orchestrator()
    
    state = await orchestrator.run_workflow(
        trigger=trigger.trigger_type,
        target_role=trigger.target_role
    )
    
    return {
        "workflow_id": state.workflow_id,
        "status": state.status.value,
        "risk_event": state.risk_event.dict() if state.risk_event else None,
        "validation_passed": state.validation_passed,
        "validation_errors": state.validation_errors,
        "action_card": state.proposed_action.dict() if state.proposed_action else None,
        "final_output": state.final_output,
        "agent_history": state.agent_history,
        "iterations": state.iteration,
    }


@router.get("/workflow/{workflow_id}")
async def get_workflow_status(workflow_id: str) -> Dict[str, Any]:
    """
    Get status of a specific workflow.
    """
    orchestrator = get_orchestrator()
    state = await orchestrator.get_workflow_status(workflow_id)
    
    if not state:
        raise HTTPException(status_code=404, detail=f"Workflow {workflow_id} not found")
    
    return {
        "workflow_id": state.workflow_id,
        "status": state.status.value,
        "current_agent": state.current_agent.value if state.current_agent else None,
        "iteration": state.iteration,
        "validation_passed": state.validation_passed,
        "created_at": state.created_at.isoformat(),
    }


@router.post("/workflow/{workflow_id}/approve")
async def approve_workflow(workflow_id: str, approval: ActionApproval) -> Dict[str, Any]:
    """
    Approve or reject a pending workflow action.
    """
    orchestrator = get_orchestrator()
    
    if approval.approved:
        success = await orchestrator.approve_action(workflow_id)
        action = "approved"
    else:
        success = await orchestrator.reject_action(workflow_id, approval.reason or "No reason given")
        action = "rejected"
    
    if not success:
        raise HTTPException(
            status_code=400, 
            detail="Workflow not in awaiting_approval state or not found"
        )
    
    return {
        "workflow_id": workflow_id,
        "action": action,
        "success": success,
    }


@router.get("/workflows")
async def list_workflows() -> Dict[str, Any]:
    """
    List all active workflows.
    """
    orchestrator = get_orchestrator()
    
    workflows = []
    for wf_id, state in orchestrator.active_workflows.items():
        workflows.append({
            "workflow_id": wf_id,
            "status": state.status.value,
            "risk_event_type": state.risk_event.event_type if state.risk_event else None,
            "created_at": state.created_at.isoformat(),
        })
    
    return {
        "count": len(workflows),
        "workflows": workflows,
    }


@router.get("/agents")
async def list_agents() -> Dict[str, Any]:
    """
    List all agents and their roles.
    """
    return {
        "agents": [
            {
                "name": "Monitor Agent",
                "type": "monitor",
                "role": "Risk Detection",
                "description": "Monitors forecasts and patient data for risk thresholds",
            },
            {
                "name": "Retrieval Agent",
                "type": "retrieval",
                "role": "Context Fetching",
                "description": "Retrieves relevant SOPs and guidelines from RAG",
            },
            {
                "name": "Planning Agent",
                "type": "planning",
                "role": "Action Generation",
                "description": "LLM-powered agent that generates ActionCards",
            },
            {
                "name": "Guardrail Agent",
                "type": "guardrail",
                "role": "Validation",
                "description": "Validates plans against safety rules and policies",
            },
            {
                "name": "Notifier Agent",
                "type": "notifier",
                "role": "Communication",
                "description": "Formats ActionCards for different user roles",
            },
        ]
    }


@router.get("/status")
async def agents_status() -> Dict[str, Any]:
    """Get agents system status."""
    orchestrator = get_orchestrator()
    
    # Check Ollama availability
    from ..agents.orchestrator import OllamaClient
    ollama = OllamaClient()
    ollama_available = await ollama.is_available()
    
    return {
        "status": "operational",
        "framework": "LangGraph-style State Machine",
        "agents_count": 5,
        "llm": {
            "provider": "Ollama",
            "model": "llama3.2:1b",
            "available": ollama_available,
            "fallback_enabled": True,
        },
        "active_workflows": len(orchestrator.active_workflows),
        "features": {
            "risk_detection": True,
            "rag_retrieval": True,
            "action_planning": True,
            "guardrail_validation": True,
            "role_based_notifications": True,
        }
    }
