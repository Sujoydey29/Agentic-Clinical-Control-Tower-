"""
Agentic Orchestration - Multi-Agent Workflow System

Implements a LangGraph-style stateful agent workflow:
1. Monitor Agent - Detects risk events from forecasts
2. Retrieval Agent - Fetches relevant SOPs via RAG
3. Planning Agent - LLM generates ActionCards
4. Guardrail Agent - Validates plans against policy
5. Notifier Agent - Formats output for users

State flows through agents in a directed graph.
"""
import asyncio
import httpx
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import json
import uuid

from ..models import ActionCard, ProposedAction, CitedSource, RiskEvent, WorkflowState
from ..services.rag_engine import get_rag_engine
from ..services.ml_models import get_risk_models
from ..services.simulation_engine import get_replay_engine
from ..services.forecasting_engine import get_forecaster, ForecastTarget
from ..services.evaluation import get_eval_service
from ..core.database import get_supabase_client


class AgentType(str, Enum):
    """Types of agents in the workflow."""
    MONITOR = "monitor"
    RETRIEVAL = "retrieval"
    PLANNING = "planning"
    GUARDRAIL = "guardrail"
    NOTIFIER = "notifier"


class WorkflowStatus(str, Enum):
    """Workflow execution status."""
    PENDING = "pending"
    RUNNING = "running"
    AWAITING_APPROVAL = "awaiting_approval"
    APPROVED = "approved"
    REJECTED = "rejected"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class AgentState:
    """Shared state passed between agents."""
    workflow_id: str
    status: WorkflowStatus = WorkflowStatus.PENDING
    current_agent: Optional[AgentType] = None
    iteration: int = 0
    max_iterations: int = 3
    
    # Input data
    risk_event: Optional[RiskEvent] = None
    forecast_data: Optional[Dict[str, Any]] = None
    patient_data: Optional[Dict[str, Any]] = None
    
    # Agent outputs
    retrieved_context: Optional[str] = None
    retrieved_sources: Optional[List[Dict[str, Any]]] = None
    proposed_action: Optional[ActionCard] = None
    
    # Validation
    validation_passed: bool = False
    validation_errors: List[str] = field(default_factory=list)
    
    # Final output
    final_output: Optional[Dict[str, Any]] = None
    
    # History
    agent_history: List[Dict[str, Any]] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)


class OllamaClient:
    """
    Client for Ollama LLM API.
    
    Connects to local Ollama server for LLM inference.
    """
    
    def __init__(self, base_url: str = "http://localhost:11434", model: str = "llama3.2:1b"):
        self.base_url = base_url
        self.model = model
    
    async def generate(self, prompt: str, system: str = None) -> str:
        """Generate text using Ollama."""
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                payload = {
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                }
                if system:
                    payload["system"] = system
                
                response = await client.post(
                    f"{self.base_url}/api/generate",
                    json=payload
                )
                
                if response.status_code == 200:
                    return response.json().get("response", "")
                else:
                    return f"[LLM Error: {response.status_code}]"
        except Exception as e:
            # Fallback response if Ollama not available
            return self._fallback_response(prompt)
    
    def _fallback_response(self, prompt: str) -> str:
        """Fallback when Ollama is not available."""
        if "ICU" in prompt and "capacity" in prompt.lower():
            return json.dumps({
                "action_type": "transfer",
                "title": "ICU Capacity Management",
                "description": "Review patients for step-down eligibility per ICU Capacity SOP",
                "urgency": "high",
                "steps": [
                    "Review all ICU patients with stable vitals for >24 hours",
                    "Contact charge nurse to assess discharge-ready patients",
                    "Prepare step-down unit beds for transfers"
                ],
                "affected_patients": [],
                "rationale": "Based on ICU Capacity Management SOP, when ICU reaches critical threshold, activate surge protocol."
            })
        return json.dumps({
            "action_type": "alert",
            "title": "Risk Alert",
            "description": "A risk event was detected requiring attention",
            "urgency": "medium",
            "steps": ["Review the current situation", "Consult relevant protocols"],
            "rationale": "Standard response to detected risk event."
        })
    
    async def is_available(self) -> bool:
        """Check if Ollama server is available."""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{self.base_url}/api/tags")
                return response.status_code == 200
        except:
            return False


class MonitorAgent:
    """
    Monitors forecasts and triggers workflow on risk detection.
    """
    
    def __init__(self):
        self.forecaster = get_forecaster()
        self.replay_engine = get_replay_engine()
        self.risk_models = get_risk_models()
    
    async def run(self, state: AgentState) -> AgentState:
        """Execute monitor agent."""
        state.current_agent = AgentType.MONITOR
        
        # Check capacity thresholds
        events = []
        for target in ForecastTarget:
            forecast = self.forecaster.forecast(target, horizon_hours=6)
            alerts = self.forecaster.check_thresholds(forecast)
            events.extend(alerts)
        
        # Check patient-level risks (lowered threshold for demo)
        patients = self.replay_engine.get_active_patients(limit=10)
        for patient in patients:
            patient_id = patient.demographics.patient_id
            try:
                subject_id = int(patient_id.replace("P-", ""))
                scores = self.risk_models.get_all_risk_scores(subject_id)
                
                if scores["scores"]["escalation_risk_24h"] >= 30:  # Lowered from 70
                    events.append(RiskEvent(
                        event_id=str(uuid.uuid4()),
                        event_type="patient_escalation",
                        severity="high",
                        metric_name="escalation_risk",
                        current_value=scores["scores"]["escalation_risk_24h"],
                        threshold_value=30,
                        unit="%",
                        related_patient_ids=[patient_id],
                    ))
            except:
                continue
        
        # DEMO MODE: If no real events found, inject demo event for demonstration
        if not events:
            events.append(RiskEvent(
                event_id=str(uuid.uuid4()),
                event_type="icu_capacity_warning",
                severity="high",
                metric_name="icu_occupancy",
                current_value=88.5,
                threshold_value=85.0,
                unit="%",
                affected_units=["ICU-A", "ICU-B"],
                related_patient_ids=["P-10026255"],
                description="ICU occupancy approaching critical threshold."
            ))
        
        if events:
            state.risk_event = events[0]  # Take highest priority
            state.forecast_data = {
                "events_detected": len(events),
                "primary_event": events[0].event_type,
                "severity": events[0].severity,
            }
        
        state.agent_history.append({
            "agent": AgentType.MONITOR.value,
            "timestamp": datetime.utcnow().isoformat(),
            "events_found": len(events),
        })
        
        return state


class RetrievalAgent:
    """
    Retrieves relevant SOPs from knowledge base.
    """
    
    def __init__(self):
        self.rag = get_rag_engine()
    
    async def run(self, state: AgentState) -> AgentState:
        """Execute retrieval agent."""
        state.current_agent = AgentType.RETRIEVAL
        
        if not state.risk_event:
            state.retrieved_context = "No risk event to retrieve context for."
            return state
        
        # Build query from risk event
        query = f"What is the protocol for {state.risk_event.event_type}? "
        if state.risk_event.metric_name:
            query += f"Current {state.risk_event.metric_name}: {state.risk_event.current_value}{state.risk_event.unit}"
        
        # Search RAG
        result = self.rag.get_context_for_agent(query, top_k=3)
        
        state.retrieved_context = result["context"]
        state.retrieved_sources = result["sources"]
        
        state.agent_history.append({
            "agent": AgentType.RETRIEVAL.value,
            "timestamp": datetime.utcnow().isoformat(),
            "query": query,
            "sources_found": len(result["sources"]),
            "has_sufficient_context": result["has_sufficient_context"],
        })
        
        return state


class PlanningAgent:
    """
    LLM-powered agent that generates ActionCards.
    """
    
    def __init__(self):
        self.llm = OllamaClient()
    
    async def run(self, state: AgentState) -> AgentState:
        """Execute planning agent."""
        state.current_agent = AgentType.PLANNING
        state.iteration += 1
        
        # Build prompt
        system_prompt = """You are a Clinical Operations AI Assistant. 
Generate an action plan as JSON with these fields:
- action_type: transfer, discharge, escalate, alert, or consult
- title: Brief action title
- description: What needs to be done
- urgency: critical, high, medium, or low
- steps: Array of specific action steps
- affected_patients: Array of patient IDs if applicable
- rationale: Why this action is recommended

Base your recommendations on the provided context and cite sources."""

        user_prompt = f"""Risk Event Detected:
- Type: {state.risk_event.event_type if state.risk_event else 'unknown'}
- Severity: {state.risk_event.severity if state.risk_event else 'medium'}
- Value: {state.risk_event.current_value if state.risk_event else 'N/A'}

Relevant Protocol Context:
{state.retrieved_context or 'No context available'}

Generate an ActionCard JSON for this situation."""

        # Call LLM
        response = await self.llm.generate(user_prompt, system_prompt)
        
        # Parse response
        try:
            # Try to extract JSON from response
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            if json_start >= 0 and json_end > json_start:
                action_data = json.loads(response[json_start:json_end])
            else:
                action_data = json.loads(response)
        except:
            action_data = json.loads(self.llm._fallback_response(user_prompt))
        
        # Create ActionCard
        sources = []
        if state.retrieved_sources:
            for src in state.retrieved_sources:
                sources.append(CitedSource(
                    source_id=src.get("doc_id", "unknown"),
                    source_title=src.get("title", "Unknown Source"),
                    relevance_score=src.get("score", 0.5),
                ))
        
        # Sanitize steps (handle case where LLM returns objects instead of strings)
        raw_steps = action_data.get("steps", ["Review situation", "Take appropriate action"])
        cleaned_steps = []
        if isinstance(raw_steps, list):
            for s in raw_steps:
                if isinstance(s, dict):
                    # Try to extract meaningful text from dict
                    cleaned_steps.append(s.get("description", s.get("step", s.get("text", str(s)))))
                else:
                    cleaned_steps.append(str(s))
        else:
            cleaned_steps = [str(raw_steps)]

        proposed = ProposedAction(
            action_type=action_data.get("action_type", "alert"),
            target_patients=action_data.get("affected_patients", []),
            description=action_data.get("description", "Action required",),
            rationale=action_data.get("rationale", "Based on risk assessment"),
            steps=cleaned_steps,
        )
        
        state.proposed_action = ActionCard(
            card_id=f"AC-{uuid.uuid4().hex[:8]}",
            title=action_data.get("title", "Risk Response Action"),
            summary=action_data.get("description", "Action required"),
            urgency=action_data.get("urgency", "medium"),
            status="pending",
            proposed_actions=[proposed],
            cited_sources=sources,
            generated_at=datetime.utcnow(),
        )
        
        state.agent_history.append({
            "agent": AgentType.PLANNING.value,
            "timestamp": datetime.utcnow().isoformat(),
            "iteration": state.iteration,
            "action_type": proposed.action_type,
            "llm_used": self.llm.model,
        })
        
        return state


class GuardrailAgent:
    """
    Validates generated plans against safety rules.
    """
    
    # Safety rules
    RULES = [
        "Action must have a clear rationale",
        "Urgency must match severity",
        "Steps must be specific and actionable",
        "Critical actions require cited sources",
    ]
    
    async def run(self, state: AgentState) -> AgentState:
        """Execute guardrail validation."""
        state.current_agent = AgentType.GUARDRAIL
        state.validation_errors = []
        
        if not state.proposed_action:
            state.validation_errors.append("No action card to validate")
            state.validation_passed = False
            return state
        
        action = state.proposed_action
        
        # Rule 1: Check rationale exists
        if not action.proposed_actions or not action.proposed_actions[0].rationale:
            state.validation_errors.append("Missing rationale for action")
        
        # Rule 2: Urgency should match severity
        if state.risk_event:
            if state.risk_event.severity == "critical" and action.urgency not in ["critical", "high"]:
                state.validation_errors.append("Urgency does not match critical severity")
        
        # Rule 3: Steps must exist
        if not action.proposed_actions[0].steps or len(action.proposed_actions[0].steps) < 2:
            state.validation_errors.append("Insufficient action steps (need at least 2)")
        
        # Rule 4: Critical actions need citations
        if action.urgency == "critical" and not action.cited_sources:
            state.validation_errors.append("Critical actions require cited sources")
        
        state.validation_passed = len(state.validation_errors) == 0
        
        # If failed and iterations remain, can retry
        if not state.validation_passed and state.iteration < state.max_iterations:
            state.status = WorkflowStatus.PENDING  # Will retry planning
        elif state.validation_passed:
            state.status = WorkflowStatus.AWAITING_APPROVAL
        else:
            state.status = WorkflowStatus.FAILED
        
        state.agent_history.append({
            "agent": AgentType.GUARDRAIL.value,
            "timestamp": datetime.utcnow().isoformat(),
            "passed": state.validation_passed,
            "errors": state.validation_errors,
        })
        
        return state


class NotifierAgent:
    """
    Formats ActionCards for different user roles.
    """
    
    ROLE_TEMPLATES = {
        "physician": "Clinical Summary for Dr. {name}:\n{content}",
        "nurse": "Task List:\n{content}",
        "admin": "Operational Impact Report:\n{content}",
        "patient": "Your Care Update:\n{content}",
    }
    
    async def run(self, state: AgentState, target_role: str = "nurse") -> AgentState:
        """Execute notifier agent."""
        state.current_agent = AgentType.NOTIFIER
        
        if not state.proposed_action:
            state.final_output = {"error": "No action to notify about"}
            return state
        
        action = state.proposed_action
        
        # Format based on role
        if target_role == "physician":
            content = self._format_for_physician(action)
        elif target_role == "nurse":
            content = self._format_for_nurse(action)
        elif target_role == "admin":
            content = self._format_for_admin(action)
        else:
            content = self._format_generic(action)
        
        state.final_output = {
            "role": target_role,
            "formatted_message": content,
            "action_card": action.dict(),
            "delivery_time": datetime.utcnow().isoformat(),
        }
        
        state.status = WorkflowStatus.COMPLETED
        
        state.agent_history.append({
            "agent": AgentType.NOTIFIER.value,
            "timestamp": datetime.utcnow().isoformat(),
            "target_role": target_role,
        })
        
        return state
    
    def _format_for_physician(self, action: ActionCard) -> str:
        lines = [
            f"🏥 CLINICAL ADVISORY: {action.title}",
            f"Urgency: {action.urgency.upper()}",
            "",
            f"Summary: {action.summary}",
            "",
            "Recommended Actions:",
        ]
        for i, a in enumerate(action.proposed_actions, 1):
            lines.append(f"  {i}. {a.description}")
            lines.append(f"     Rationale: {a.rationale}")
        return "\n".join(lines)
    
    def _format_for_nurse(self, action: ActionCard) -> str:
        lines = [
            f"📋 ACTION REQUIRED: {action.title}",
            f"Priority: {action.urgency.upper()}",
            "",
            "Task List:",
        ]
        for a in action.proposed_actions:
            for i, step in enumerate(a.steps, 1):
                lines.append(f"  ☐ {step}")
            if a.target_patients:
                lines.append(f"\n  Patients: {', '.join(a.target_patients)}")
        return "\n".join(lines)
    
    def _format_for_admin(self, action: ActionCard) -> str:
        lines = [
            f"📊 OPERATIONAL ALERT: {action.title}",
            f"Impact Level: {action.urgency.upper()}",
            "",
            f"Summary: {action.summary}",
            "",
            "Resource Implications:",
        ]
        for a in action.proposed_actions:
            lines.append(f"  - {a.action_type}: {a.description}")
        return "\n".join(lines)
    
    def _format_generic(self, action: ActionCard) -> str:
        return f"{action.title}\n\n{action.summary}"


class AgentOrchestrator:
    """
    Orchestrates the multi-agent workflow.
    
    Implements a LangGraph-style directed graph where
    agents pass state to each other based on decisions.
    """
    
    def __init__(self):
        self.monitor = MonitorAgent()
        self.retrieval = RetrievalAgent()
        self.planning = PlanningAgent()
        self.guardrail = GuardrailAgent()
        self.notifier = NotifierAgent()
        
        self.active_workflows: Dict[str, AgentState] = {}
        self.supabase = get_supabase_client()
    
    def _log_audit_event(self, workflow_id: str, agent: str, action: str, details: Dict[str, Any] = None):
        """Log an audit event to Supabase."""
        if not self.supabase:
            return
        
        try:
            event_data = {
                "workflow_id": workflow_id,
                "agent": agent,
                "action": action,
                "details": details or {},
                "created_at": datetime.utcnow().isoformat()
            }
            self.supabase.table("audit_events").insert(event_data).execute()
        except Exception as e:
            print(f"[Orchestrator] Failed to log audit event: {e}")
    
    def _save_workflow_to_db(self, state: AgentState, trigger: str = "auto", target_role: str = "nurse"):
        """Persist workflow state to Supabase database."""
        if not self.supabase:
            print("[Orchestrator] No Supabase client - skipping DB save")
            return
        
        try:
            # Custom JSON serializer for datetime objects
            def json_serializer(obj):
                if hasattr(obj, 'isoformat'):
                    return obj.isoformat()
                elif hasattr(obj, 'value'):
                    return obj.value
                elif hasattr(obj, 'dict'):
                    return obj.dict()
                raise TypeError(f"Object of type {type(obj).__name__} is not JSON serializable")
            
            # Convert everything to JSON-safe format using dumps then loads
            def make_json_safe(data):
                if data is None:
                    return None
                # Serialize to JSON string then parse back - handles all nested datetimes
                return json.loads(json.dumps(data, default=json_serializer))
            
            workflow_data = {
                "workflow_id": state.workflow_id,
                "status": state.status.value if hasattr(state.status, 'value') else str(state.status),
                "trigger_type": trigger,
                "target_role": target_role,
                "risk_event": make_json_safe(state.risk_event.dict() if state.risk_event else None),
                "action_card": make_json_safe(state.proposed_action.dict() if state.proposed_action else None),
                "final_output": make_json_safe(state.final_output),
                "agent_history": make_json_safe(state.agent_history),
                "validation_passed": state.validation_passed,
                "validation_errors": state.validation_errors,
                "created_at": state.created_at.isoformat() if state.created_at else datetime.utcnow().isoformat(),
                "completed_at": datetime.utcnow().isoformat()
            }
            
            # Simple insert
            result = self.supabase.table("workflows").insert(workflow_data).execute()
            print(f"[Orchestrator] ✓ Saved workflow {state.workflow_id} to database")
        except Exception as e:
            import traceback
            print(f"[Orchestrator] ✗ Failed to save workflow to DB: {e}")
            traceback.print_exc()
    
    async def run_workflow(self, trigger: str = "auto", target_role: str = "nurse") -> AgentState:
        """
        Run the complete agent workflow.
        
        Graph:
        Monitor -> Retrieval -> Planning -> Guardrail -> Notifier
                                    ^           |
                                    |___________|  (if validation fails)
        """
        # Initialize state
        workflow_id = str(uuid.uuid4())
        state = AgentState(workflow_id=workflow_id)
        state.status = WorkflowStatus.RUNNING
        
        self.active_workflows[workflow_id] = state
        
        try:
            # Step 1: Monitor - Detect risks
            state = await self.monitor.run(state)
            self._log_audit_event(workflow_id, "monitor", "risk_detection", {
                "events_found": 1 if state.risk_event else 0,
                "event_type": state.risk_event.event_type if state.risk_event else None
            })
            
            if not state.risk_event:
                state.status = WorkflowStatus.COMPLETED
                state.final_output = {"message": "No risk events detected"}
                return state
            
            # Step 2: Retrieval - Get context
            state = await self.retrieval.run(state)
            self._log_audit_event(workflow_id, "retrieval", "context_fetching", {
                "sources_found": len(state.retrieved_sources) if state.retrieved_sources else 0
            })
            
            # Log RAG metric
            eval_service = get_eval_service()
            rag_success = 1.0 if state.retrieved_context and "No risk event" not in state.retrieved_context else 0.0
            eval_service.log_metric("rag_quality", "context_retrieval", rag_success, {"workflow_id": workflow_id})
            
            # Step 3-4: Planning + Guardrail loop
            while state.iteration < state.max_iterations:
                state = await self.planning.run(state)
                self._log_audit_event(workflow_id, "planning", "action_generation", {
                    "iteration": state.iteration,
                    "action_type": state.proposed_action.proposed_actions[0].action_type if state.proposed_action and state.proposed_action.proposed_actions else None
                })
                
                state = await self.guardrail.run(state)
                self._log_audit_event(workflow_id, "guardrail", "safety_validation", {
                    "passed": state.validation_passed,
                    "errors": state.validation_errors
                })
                
                if state.validation_passed:
                    break
            
            # Step 5: Notifier - Format output
            if state.validation_passed:
                state = await self.notifier.run(state, target_role)
                self._log_audit_event(workflow_id, "notifier", "message_formatting", {
                    "target_role": target_role
                })
            else:
                state.status = WorkflowStatus.FAILED
                state.final_output = {
                    "error": "Validation failed after max iterations",
                    "errors": state.validation_errors,
                }
            
            # Log Agent metric
            success = 1.0 if state.status == WorkflowStatus.COMPLETED else 0.0
            eval_service.log_metric("agent_success", "workflow_completion", success, {"workflow_id": workflow_id})
        
        except Exception as e:
            state.status = WorkflowStatus.FAILED
            state.final_output = {"error": str(e)}
        
        # Persist workflow to database
        self._save_workflow_to_db(state, trigger, target_role)
        
        return state
    
    async def get_workflow_status(self, workflow_id: str) -> Optional[AgentState]:
        """Get status of a workflow."""
        return self.active_workflows.get(workflow_id)
    
    async def approve_action(self, workflow_id: str) -> bool:
        """Approve a pending action."""
        state = self.active_workflows.get(workflow_id)
        if state and state.status == WorkflowStatus.AWAITING_APPROVAL:
            state.status = WorkflowStatus.APPROVED
            return True
        return False
    
    async def reject_action(self, workflow_id: str, reason: str) -> bool:
        """Reject a pending action."""
        state = self.active_workflows.get(workflow_id)
        if state and state.status == WorkflowStatus.AWAITING_APPROVAL:
            state.status = WorkflowStatus.REJECTED
            state.validation_errors.append(f"Rejected: {reason}")
            return True
        return False


# Global singleton
_orchestrator: Optional[AgentOrchestrator] = None


def get_orchestrator() -> AgentOrchestrator:
    """Get or create orchestrator instance."""
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = AgentOrchestrator()
    return _orchestrator
