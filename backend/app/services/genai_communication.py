"""
Generative AI Communication Layer.

Handles the generation of role-specific messages, reports, and simulated scenarios
using LLM prompts templates and the ActionCard data.
"""
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from enum import Enum
import httpx

from ..models import ActionCard, RiskEvent
from ..agents.orchestrator import OllamaClient


class TargetRole(str, Enum):
    """User roles for targeted communication."""
    PHYSICIAN = "physician"
    NURSE = "nurse"
    ADMIN = "admin"
    PATIENT = "patient"


class PromptTemplates:
    """Prompt templates for different roles and tasks."""
    
    PHYSICIAN_MSG = """
    Target Audience: Physician (Clinical Focus)
    Task: Convert the following Action Plan into a concise clinical advisory.
    Style: Professional, concise, medical terminology, SBAR format (Situation, Background, Assessment, Recommendation).
    
    Action Plan:
    {action_json}
    
    Output Format:
    - **SITUATION**: [Brief summary of risk]
    - **BACKGROUND**: [Context if available]
    - **ASSESSMENT**: [Risk severity and key metrics]
    - **RECOMMENDATION**: [Specific actions]
    """
    
    NURSE_MSG = """
    Target Audience: Charge Nurse (Operational Focus)
    Task: Convert the following Action Plan into a prioritized task list.
    Style: Direct, action-oriented, checklist format.
    
    Action Plan:
    {action_json}
    
    Output Format:
    **URGENT TASKS:**
    1. [First action]
    ...
    
    **CONTEXT:** [Brief reason]
    **PROTOCOLS:** [Mentioned SOPs]
    """
    
    ADMIN_MSG = """
    Target Audience: Hospital Administrator (Resource Focus)
    Task: Summarize the operational impact of this event.
    Style: Formal, high-level, resource-centric (beds, staff, cost).
    
    Action Plan:
    {action_json}
    
    Output Format:
    **EXECUTIVE SUMMARY**: [What is happening]
    **RESOURCE IMPACT**: [Units/Staff affected]
    **REQUIRED DECISIONS**: [Approvals needed]
    """
    
    PATIENT_MSG = """
    Target Audience: Patient/Family (Layman Focus)
    Task: Explain the situation in simple, reassuring language.
    Style: Empathetic, clear (Grade 6 reading level), avoiding jargon.
    
    Action Plan:
    {action_json}
    
    Risk Context:
    {risk_json}
    
    Output:
    "Dear Patient/Family,
    
    [Explanation of what is happening (e.g., unit is busy)]
    [What we are doing (e.g., moving you to a quieter room)]
    [Assurance of continued care]"
    """
    
    SHIFT_REPORT = """
    Task: Generate a Shift Handoff Report for the incoming team.
    Time Range: {time_range}
    
    Events Log:
    {events_log}
    
    Output Format:
    # 🏥 Shift Handoff Report
    **Status**: [Green/Yellow/Red based on severity]
    
    ## 🚩 Major Events
    - [Time]: [Event] (Action Taken)
    
    ## 📊 Current Risks
    - [Active risks]
    
    ## 📝 Pending Actions
    - [List of pending/uncompleted steps]
    """


class CommunicationService:
    """Service for generating AI-powered communications."""
    
    def __init__(self):
        self.llm = OllamaClient()
    
    async def generate_message(self, action_card: ActionCard, role: TargetRole, risk_event: Optional[RiskEvent] = None) -> str:
        """
        Generate a role-specific message for an ActionCard.
        """
        # Serialize inputs
        action_json = action_card.json(exclude_none=True)
        risk_json = risk_event.json() if risk_event else "{}"
        
        # Select prompt
        system_prompt = "You are an expert medical communication assistant."
        
        if role == TargetRole.PHYSICIAN:
            prompt = PromptTemplates.PHYSICIAN_MSG.format(action_json=action_json)
        elif role == TargetRole.NURSE:
            prompt = PromptTemplates.NURSE_MSG.format(action_json=action_json)
        elif role == TargetRole.ADMIN:
            prompt = PromptTemplates.ADMIN_MSG.format(action_json=action_json)
        elif role == TargetRole.PATIENT:
            prompt = PromptTemplates.PATIENT_MSG.format(action_json=action_json, risk_json=risk_json)
            system_prompt += " Use plain language. Be empathetic."
        else:
            return f"Role {role} not supported."
        
        # Generate
        response = await self.llm.generate(prompt, system_prompt)
        return response
    
    async def generate_shift_report(self, events: List[Dict[str, Any]], hours: int = 12) -> str:
        """Generates a summary report of recent events."""
        time_range = f"Last {hours} hours"
        events_json = json.dumps(events, indent=2, default=str)
        
        prompt = PromptTemplates.SHIFT_REPORT.format(
            time_range=time_range,
            events_log=events_json
        )
        
        response = await self.llm.generate(prompt, system="You are a clinical supervisor creating a handoff report.")
        return response

    async def simulate_scenario(self, scenario_description: str) -> Dict[str, Any]:
        """
        Run a 'What-If' simulation analysis.
        This asks the LLM to predict cascade effects of a scenario.
        """
        prompt = f"""
        Scenario Simulation:
        "{scenario_description}"
        
        Given a hospital environment with constrained ICU and ER capacity, 
        predict the likely cascade of effects from this scenario.
        
        Output JSON:
        {{
            "predicted_impact": "string description",
            "risk_level_change": "low/medium/high/critical",
            "recommended_preparations": ["step 1", "step 2"]
        }}
        """
        
        response = await self.llm.generate(prompt)
        
        try:
            # Extract JSON
            start = response.find("{")
            end = response.rfind("}") + 1
            if start >= 0:
                data = json.loads(response[start:end])
                return data
            return {"error": "Could not parse simulation result", "raw": response}
        except:
            return {"error": "Simulation failed", "raw": response}


# Singleton
_comm_service: Optional[CommunicationService] = None

def get_comm_service() -> CommunicationService:
    global _comm_service
    if _comm_service is None:
        _comm_service = CommunicationService()
    return _comm_service
