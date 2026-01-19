"""
Evaluation & Safety Layer (The Trust Engine).

Handles:
1. Metrics logging (ML, RAG, Agent performance).
2. Human Feedback collection (HITL).
3. Audit Trail aggregation.

NOW WITH SUPABASE PERSISTENCE.
"""
from typing import Dict, List, Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field
from enum import Enum
import json

from ..core.database import get_supabase_client


class FeedbackType(str, Enum):
    """Types of user feedback."""
    THUMBS_UP = "thumbs_up"
    THUMBS_DOWN = "thumbs_down"
    EDITED = "edited"


class EvaluationService:
    """Service for tracking system performance and safety with Supabase persistence."""
    
    def __init__(self):
        self.supabase = get_supabase_client()
    
    def log_metric(self, category: str, name: str, value: float, metadata: Dict[str, Any] = None):
        """Log a performance metric to database."""
        entry = {
            "category": category,
            "metric_name": name,
            "value": value,
            "metadata": metadata or {},
            "created_at": datetime.utcnow().isoformat()
        }
        
        # Try to persist to Supabase
        if self.supabase:
            try:
                self.supabase.table("metrics").insert(entry).execute()
            except Exception as e:
                print(f"[EvalService] Failed to log metric to DB: {e}")
    
    def submit_feedback(self, workflow_id: str, feedback_type: str, comments: Optional[str] = None, user_role: str = "unknown"):
        """Collect human feedback on a workflow result."""
        entry = {
            "workflow_id": workflow_id,
            "feedback_type": feedback_type,
            "comments": comments,
            "user_role": user_role,
            "created_at": datetime.utcnow().isoformat()
        }
        
        # Persist to Supabase
        if self.supabase:
            try:
                self.supabase.table("feedback").insert(entry).execute()
            except Exception as e:
                print(f"[EvalService] Failed to save feedback to DB: {e}")
        
        # Also log as a metric
        if feedback_type == FeedbackType.THUMBS_DOWN:
            self.log_metric("agent_success", "workflow_quality", 0.0, {"workflow_id": workflow_id})
        elif feedback_type == FeedbackType.THUMBS_UP:
            self.log_metric("agent_success", "workflow_quality", 1.0, {"workflow_id": workflow_id})
    
    def log_audit_event(self, workflow_id: str, agent: str, action: str, details: Dict[str, Any] = None):
        """Log an audit event for a workflow."""
        entry = {
            "workflow_id": workflow_id,
            "agent": agent,
            "action": action,
            "details": details or {},
            "created_at": datetime.utcnow().isoformat()
        }
        
        if self.supabase:
            try:
                self.supabase.table("audit_events").insert(entry).execute()
            except Exception as e:
                print(f"[EvalService] Failed to log audit event to DB: {e}")

    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get summary statistics of current metrics from database."""
        summary = {}
        categories = ["ml_accuracy", "rag_quality", "agent_success"]
        
        if self.supabase:
            try:
                for category in categories:
                    result = self.supabase.table("metrics").select("*").eq("category", category).execute()
                    entries = result.data if result.data else []
                    
                    if not entries:
                        summary[category] = {"count": 0, "avg": 0.0}
                        continue
                    
                    values = [e["value"] for e in entries]
                    summary[category] = {
                        "count": len(values),
                        "avg": sum(values) / len(values) if values else 0,
                        "min": min(values) if values else 0,
                        "max": max(values) if values else 0,
                        "latest_entry": entries[-1] if entries else None
                    }
            except Exception as e:
                print(f"[EvalService] Failed to get metrics: {e}")
                summary = {c: {"count": 0, "avg": 0.0, "error": str(e)} for c in categories}
        else:
            summary = {c: {"count": 0, "avg": 0.0, "note": "Database not configured"} for c in categories}
        
        return summary

    def get_audit_trail(self, workflow_id: str) -> Dict[str, Any]:
        """
        Reconstruct full audit trail for a workflow from database.
        """
        # First try to get from database
        if self.supabase:
            try:
                # Get workflow
                workflow_result = self.supabase.table("workflows").select("*").eq("workflow_id", workflow_id).execute()
                
                if workflow_result.data:
                    workflow = workflow_result.data[0]
                    
                    # Get audit events
                    audit_result = self.supabase.table("audit_events").select("*").eq("workflow_id", workflow_id).order("created_at").execute()
                    
                    # Get feedback
                    feedback_result = self.supabase.table("feedback").select("*").eq("workflow_id", workflow_id).execute()
                    
                    return {
                        "workflow_id": workflow["workflow_id"],
                        "status": workflow["status"],
                        "created_at": workflow["created_at"],
                        "timeline": workflow.get("agent_history", []),
                        "audit_events": audit_result.data if audit_result.data else [],
                        "final_output": workflow.get("final_output"),
                        "feedback": feedback_result.data if feedback_result.data else []
                    }
            except Exception as e:
                print(f"[EvalService] Failed to get audit trail from DB: {e}")
        
        # Fallback to in-memory orchestrator
        from ..agents.orchestrator import get_orchestrator
        
        orch = get_orchestrator()
        workflow = orch.active_workflows.get(workflow_id)
        
        if not workflow:
            return {"error": "Workflow not found"}
            
        return {
            "workflow_id": workflow.workflow_id,
            "status": workflow.status.value if hasattr(workflow.status, 'value') else str(workflow.status),
            "created_at": workflow.created_at.isoformat() if workflow.created_at else None,
            "timeline": workflow.agent_history,
            "final_output": workflow.final_output,
            "feedback": []
        }


# Singleton
_eval_service: Optional[EvaluationService] = None

def get_eval_service() -> EvaluationService:
    global _eval_service
    if _eval_service is None:
        _eval_service = EvaluationService()
    return _eval_service
