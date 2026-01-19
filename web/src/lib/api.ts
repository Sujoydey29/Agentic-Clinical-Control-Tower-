/**
 * API Client for ACCT Backend
 * Connects to FastAPI backend on localhost:8000
 */

const API_BASE = "http://localhost:8000/api/v1";

/**
 * Generic fetch wrapper with error handling
 */
async function fetchAPI<T>(endpoint: string, options?: RequestInit): Promise<T> {
    const url = `${API_BASE}${endpoint}`;

    const response = await fetch(url, {
        ...options,
        headers: {
            "Content-Type": "application/json",
            ...options?.headers,
        },
    });

    if (!response.ok)
    {
        throw new Error(`API Error: ${response.status} ${response.statusText}`);
    }

    return response.json();
}

// ============ Patients API (Part 1) ============

export interface Patient {
    demographics: {
        patient_id: string;
        name: string;
        age: number;
        gender: string;
        admission_date: string;
        unit: string;
    };
    clinical: {
        diagnoses: string[];
        diagnosis_text: string;
        current_vitals: {
            timestamp: string;
            heart_rate: number;
            blood_pressure_systolic: number;
            blood_pressure_diastolic: number;
            spo2: number;
            respiratory_rate: number;
            temperature: number;
        };
        vitals_history: any[];
    };
    risk_scores: {
        patient_id: string;
        discharge_readiness: number;
        readmission_risk_30d: number;
        escalation_risk: number;
        expected_los_days: number;
        calculated_at: string;
    };
    status: string;
}

export async function getPatients(limit = 50): Promise<Patient[]> {
    return fetchAPI(`/patients/?limit=${limit}`);
}

export async function getPatientById(patientId: string): Promise<Patient> {
    return fetchAPI(`/patients/${patientId}`);
}

export async function getPatientRiskScores(patientId: string): Promise<any> {
    return fetchAPI(`/ml/risk/${patientId}`);
}

// ============ Forecasts API (Part 2) ============

export interface ForecastDataPoint {
    timestamp: string;
    predicted_value: number;
    lower_bound: number;
    upper_bound: number;
}

export interface CapacityForecast {
    metric_name: string;
    unit: string;
    current_value: number;
    forecast_horizon_hours: number;
    data_points: ForecastDataPoint[];
    generated_at: string;
}

export async function getIcuForecast(hours = 24): Promise<CapacityForecast> {
    return fetchAPI(`/forecasts/icu-occupancy?hours=${hours}`);
}

export async function getErForecast(hours = 24): Promise<CapacityForecast> {
    return fetchAPI(`/forecasts/er-arrivals?hours=${hours}`);
}

export async function getForecastSummary(): Promise<any> {
    return fetchAPI(`/forecasts/summary`);
}

export async function getActiveAlerts(): Promise<any[]> {
    return fetchAPI(`/forecasts/alerts`);
}

// ============ Time Series API (Part 3) ============

export interface TimeSeriesAlert {
    event_id: string;
    event_type: string;
    severity: string;
    detected_at: string;
    metric_name: string;
    current_value: number;
    threshold_value: number;
    unit: string;
    affected_units: string[];
    related_patient_ids: string[];
}

export interface CapacitySummary {
    timestamp: string;
    metrics: {
        icu_occupancy: {
            current: number;
            status: string;
            threshold_warning: number;
            threshold_critical: number;
            unit: string;
        };
        er_arrivals: {
            current: number;
            status: string;
            threshold_warning: number;
            threshold_critical: number;
            unit: string;
        };
        ward_occupancy: {
            current: number;
            status: string;
            threshold_warning: number;
            threshold_critical: number;
            unit: string;
        };
    };
    alerts: TimeSeriesAlert[];
}

export async function getTimeSeriesForecast(target: string, hours = 24): Promise<CapacityForecast> {
    return fetchAPI(`/timeseries/forecast/${target}?hours=${hours}`);
}

export async function getAllTimeSeriesForecasts(hours = 24): Promise<Record<string, CapacityForecast>> {
    return fetchAPI(`/timeseries/forecasts/all?hours=${hours}`);
}

export async function getCapacitySummary(): Promise<CapacitySummary> {
    return fetchAPI(`/timeseries/capacity/summary`);
}

export async function getTimeSeriesAlerts(): Promise<TimeSeriesAlert[]> {
    return fetchAPI(`/timeseries/alerts`);
}

export async function getTimeSeriesThresholds(): Promise<any> {
    return fetchAPI(`/timeseries/thresholds`);
}

export async function getTimeSeriesStatus(): Promise<any> {
    return fetchAPI(`/timeseries/status`);
}

// ============ NLP API (Part 4) ============

export async function processNLP(text: string): Promise<any> {
    return fetchAPI(`/nlp/process`, {
        method: "POST",
        body: JSON.stringify({ text }),
    });
}

export async function deidentifyText(text: string): Promise<any> {
    return fetchAPI(`/nlp/deidentify`, {
        method: "POST",
        body: JSON.stringify({ text }),
    });
}

export async function extractEntities(text: string): Promise<any> {
    return fetchAPI(`/nlp/extract-entities`, {
        method: "POST",
        body: JSON.stringify({ text }),
    });
}

// ============ RAG API (Part 5) ============

export interface RAGDocument {
    doc_id: string;
    title: string;
    source: string;
    doc_type: string;
    content_preview: string;
    created_at: string;
}

export interface RAGSearchResult {
    query: string;
    results: {
        chunk_id: string;
        doc_id: string;
        content: string;
        score: number;
        doc_title: string;
    }[];
    search_type: string;
    total_results: number;
}

export interface RAGStats {
    total_documents: number;
    total_chunks: number;
    embedding_model: string;
    embedding_dimension: number;
    confidence_threshold: number;
}

export async function searchKnowledge(query: string, topK = 3, searchType = "hybrid"): Promise<RAGSearchResult> {
    return fetchAPI(`/rag/search`, {
        method: "POST",
        body: JSON.stringify({ query, top_k: topK, search_type: searchType }),
    });
}

export async function getRAGDocuments(): Promise<{ count: number; documents: RAGDocument[] }> {
    return fetchAPI(`/rag/documents`);
}

export async function getRAGStats(): Promise<RAGStats> {
    return fetchAPI(`/rag/stats`);
}

export async function getRAGStatus(): Promise<any> {
    return fetchAPI(`/rag/status`);
}

// ============ Agents API (Part 6) ============

export interface WorkflowResult {
    workflow_id: string;
    status: string;
    risk_event: any;
    action_card?: any;
    final_output?: any;
    agent_history: any[];
    validation_passed: boolean;
}

export async function runAgentWorkflow(trigger = "auto", targetRole = "nurse"): Promise<WorkflowResult> {
    return fetchAPI(`/agents/run`, {
        method: "POST",
        body: JSON.stringify({ trigger_type: trigger, target_role: targetRole }),
    });
}

export async function getAgentsStatus(): Promise<any> {
    return fetchAPI(`/agents/status`);
}

export async function listAgents(): Promise<any> {
    return fetchAPI(`/agents/agents`);
}

export async function listWorkflows(): Promise<any> {
    return fetchAPI(`/agents/workflows`);
}

// ============ Communication API (Part 7) ============

export async function generateMessage(actionCard: any, role: string, riskEvent?: any): Promise<any> {
    return fetchAPI(`/communication/generate-message`, {
        method: "POST",
        body: JSON.stringify({ action_card: actionCard, role, risk_event: riskEvent }),
    });
}

export async function generateShiftReport(events: any[], hours = 12): Promise<any> {
    return fetchAPI(`/communication/shift-report`, {
        method: "POST",
        body: JSON.stringify({ events, hours }),
    });
}

export async function simulateScenario(scenario: string): Promise<any> {
    return fetchAPI(`/communication/simulate`, {
        method: "POST",
        body: JSON.stringify({ scenario }),
    });
}

// ============ Evaluation API (Part 8) ============

export async function submitFeedback(workflowId: string, feedbackType: string, comments?: string, userRole = "unknown"): Promise<any> {
    return fetchAPI(`/evaluation/feedback`, {
        method: "POST",
        body: JSON.stringify({
            workflow_id: workflowId,
            feedback_type: feedbackType,
            comments,
            user_role: userRole,
        }),
    });
}

export async function getMetrics(): Promise<any> {
    return fetchAPI(`/evaluation/metrics`);
}

export async function getAuditTrail(workflowId: string): Promise<any> {
    return fetchAPI(`/evaluation/audit/${workflowId}`);
}
