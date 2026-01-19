# Agentic Clinical Control Tower (ACCT)

**A Proactive Healthcare Operations Management System**

---

## 🏥 Project Overview

The Agentic Clinical Control Tower (ACCT) is an advanced healthcare operations management system that transforms reactive hospital workflows into proactive, AI-driven decision-making. Built as a multi-layered intelligent platform, ACCT forecasts operational demands and automatically orchestrates clinical actions in real-time.

### 🎯 Core Vision
To create the central nervous system for hospitals that anticipates operational bottlenecks and prescribes solutions before crises occur, improving patient care, staff efficiency, and resource utilization.

---

## 📋 Table of Contents

1. [Project Architecture](#project-architecture)
2. [Technology Stack](#technology-stack)
3. [System Components](#system-components)
4. [Implementation Phases](#implementation-phases)
5. [Backend Structure](#backend-structure)
6. [Frontend Structure](#frontend-structure)
7. [Getting Started](#getting-started)
8. [API Documentation](#api-documentation)
9. [Development Roadmap](#development-roadmap)

---

## 🏗️ Project Architecture

### High-Level Data Flow

```
[🏥 Hospital Data Sources] 
        ↓
[⚙️ Time-Shift Replay Engine] → Converts MIMIC-IV data to 2026 timeline
        ↓
[⚡ FastAPI Backend "The Brain"]
        ├─→ [🗄️ Supabase Database] (Persistence layer)
        ├─→ [🧩 Feature Store] (Data cleaning & validation)
        └─→ [📈 Forecasting Engine] (Predictive analytics)
        ↓
[💻 Frontend Dashboard] (Next.js 15 + TypeScript)
```

### Three-Layer Architecture

1. **_floor 1: Forecasting Layer_** - "See the Future"
   - Predicts operational metrics (ICU occupancy, ER arrivals, bed demand)
   - Uses time-series analysis and ML models

2. **_floor 2: Grounding Layer_** - "Understand the 'Why'"
   - Retrieves context from hospital knowledge base (RAG)
   - Provides explanations and supporting evidence

3. **_floor 3: Action Layer_** - "Make It Happen"
   - Intelligent agents orchestrate clinical actions
   - Generates role-specific recommendations

---

## ⚙️ Technology Stack

### Backend (Python FastAPI)
- **Framework**: FastAPI with uv package manager
- **Database**: Supabase (PostgreSQL with pgvector)
- **ML Framework**: Scikit-learn, pandas, numpy
- **NLP**: spaCy, regex-based entity extraction
- **Embeddings**: sentence-transformers (all-MiniLM-L6-v2)
- **LLM**: Ollama (llama3.2:1b for planning)
- **Orchestration**: LangGraph for agent workflows
- **Data Source**: MIMIC-IV Clinical Database (demo dataset)

### Frontend (Next.js 15)
- **Framework**: Next.js 15 with TypeScript
- **Styling**: Tailwind CSS + Shadcn UI
- **Charts**: Recharts for data visualization
- **UI Components**: Framer Motion for animations
- **Icons**: Lucide React
- **Design Theme**: "Cosmic Health" - Dark mode with neon accents

---

## 🧠 System Components

### 1. Machine Learning Engine
**Purpose**: Clinical prediction for individual patients

**Models Implemented**:
- **Discharge Readiness** (Logistic Regression): Predicts if patient can go home safely
- **Readmission Risk** (Gradient Boosting): 30-day readmission probability  
- **Length of Stay** (Linear Regression): Predicts bed occupancy duration
- **Escalation Risk** (Random Forest): Identifies patients likely to crash

**API Endpoints**:
- `GET /api/v1/ml/risk-scores/{patient_id}`
- `GET /api/v1/ml/predictions/batch`

### 2. Time Series Forecasting
**Purpose**: Operational demand prediction

**Targets**:
- ICU Occupancy (%)
- ER Arrivals (hourly counts)
- Ward Occupancy (%)

**Methodology**: ARIMA + Seasonality Decomposition
- Daily patterns (24-hour cycles)
- Weekly patterns (weekday/weekend variations)
- Trend analysis + autoregressive components

**API Endpoints**:
- `GET /api/v1/timeseries/forecast/{target}`
- `GET /api/v1/timeseries/alerts`

### 3. NLP Pipeline
**Purpose**: Process unstructured clinical text

**Capabilities**:
- Clinical Named Entity Recognition (6 entity types)
- PHI de-identification (7 PHI types)
- Text summarization and entity grouping
- Embedding preparation for RAG

**API Endpoints**:
- `POST /api/v1/nlp/process`
- `POST /api/v1/nlp/deidentify`
- `POST /api/v1/nlp/extract-entities`

### 4. RAG (Retrieval-Augmented Generation)
**Purpose**: Knowledge base for evidence-based decisions

**Features**:
- Document chunking (512 tokens with 50-token overlap)
- Vector similarity search (cosine similarity)
- Hybrid search (dense + keyword)
- Confidence threshold enforcement (0.4 minimum)

**Pre-loaded Documents**:
- ICU Capacity Management SOP
- Sepsis Management Guidelines
- Discharge Planning Guidelines

**API Endpoints**:
- `POST /api/v1/rag/search`
- `POST /api/v1/rag/documents`

### 5. Agentic Orchestration
**Purpose**: Multi-agent AI workflow coordination

**5-Agent Pipeline**:

1. **Monitor Agent** 📊
   - Watches forecasts and patient vitals
   - Detects risk events (e.g., ICU >90% occupancy)

2. **Retrieval Agent** 📚
   - Searches RAG knowledge base
   - Fetches relevant SOPs and protocols

3. **Planning Agent** 🤖
   - LLM-powered action planning
   - Generates structured ActionCards

4. **Guardrail Agent** ✓
   - Validates safety and policy compliance
   - Prevents dangerous recommendations

5. **Notifier Agent** 💬
   - Formats messages for specific roles
   - Delivers to physicians, nurses, administrators

**API Endpoints**:
- `POST /api/v1/agents/run`
- `POST /api/v1/agents/approve`

### 6. Communication Layer
**Purpose**: Human-centric message generation

**Features**:
- Role-based communication templates
- SBAR format for physicians
- Task lists for nurses
- Impact summaries for administrators
- Scenario simulation ("What-if" analysis)

**API Endpoints**:
- `POST /api/v1/communication/simulate`
- `POST /api/v1/communication/generate`

### 7. Evaluation & Safety
**Purpose**: Trust and compliance framework

**Components**:
- Hallucination control (similarity thresholds)
- Performance metrics logging
- Human-in-the-loop feedback
- Full audit trail capability

**API Endpoints**:
- `POST /api/v1/evaluation/feedback`
- `GET /api/v1/evaluation/audit`

---

## 🚀 Implementation Phases

### Phase 1: Frontend Development (Complete ✅)
- [x] Next.js 15 setup with TypeScript and Tailwind CSS
- [x] Cosmic Health design system (dark mode, glassmorphism)
- [x] Dashboard with Prophet-style charts and real-time alerts
- [x] Patient management with risk score visualization
- [x] Agentic workflow hub with stepper UI
- [x] Knowledge base search interface
- [x] Role-based communication views

### Phase 2: Backend Development

#### Part 1: Core Architecture & Data Flow ✅
- [x] FastAPI backend with Supabase integration
- [x] Time-shift replay engine for MIMIC-IV data
- [x] Feature store with Pydantic models
- [x] Forecasting API endpoints

#### Part 2: Machine Learning Engine ✅
- [x] 4 clinical prediction models implemented
- [x] Feature engineering pipeline
- [x] Risk scoring APIs

#### Part 3: Time Series Analysis ✅
- [x] ARIMA-based forecasting engine
- [x] Seasonality decomposition
- [x] Threshold-based alerting system

#### Part 4: NLP Pipeline ✅
- [x] Clinical NER and PHI detection
- [x] Text processing APIs
- [x] Embedding preparation

#### Part 5: RAG Pipeline ✅
- [x] Document ingestion and chunking
- [x] Vector store implementation
- [x] Hybrid search with re-ranking

#### Part 6: Agentic Orchestration ✅
- [x] LangGraph workflow orchestration
- [x] 5-agent pipeline implementation
- [x] Action card generation and validation

#### Part 7: Generative AI Communication ✅
- [x] Role-based message templates
- [x] Scenario simulation capabilities
- [x] Report generation

#### Part 8: Evaluation & Safety (In Progress)
- [x] Hallucination control layers
- [x] Comprehensive metrics framework
- [x] Human-in-the-loop integration

### Phase 3: Frontend Integration (In Progress)
- [x] Connect frontend to backend APIs
- [x] Real-time data synchronization
- [x] Full agent workflow integration
- [x] Evaluation feedback loops

---

## 📁 Backend Structure

```
backend/
├── app/
│   ├── agents/                 # Agent orchestration
│   │   ├── monitor_agent.py    # Risk detection
│   │   └── orchestrator.py     # Workflow coordination
│   ├── api/                    # API endpoints
│   │   ├── agents.py          # Agent workflow APIs
│   │   ├── communication.py   # Message generation
│   │   ├── evaluation.py      # Feedback and audit
│   │   ├── forecasts.py       # Forecasting endpoints
│   │   ├── ml.py             # ML model APIs
│   │   ├── nlp.py            # NLP processing
│   │   ├── patients.py       # Patient data
│   │   ├── rag.py            # RAG search
│   │   └── timeseries.py     # Time series APIs
│   ├── core/                  # Core utilities
│   │   ├── config.py         # Configuration
│   │   ├── database.py       # DB connections
│   │   └── __init__.py
│   ├── models/                # Data models
│   │   ├── agents.py         # Agent schemas
│   │   ├── patient.py        # Patient models
│   │   └── __init__.py
│   ├── services/              # Business logic
│   │   ├── evaluation.py     # Metrics tracking
│   │   ├── feature_store.py  # Data processing
│   │   ├── forecasting_engine.py # TS forecasting
│   │   ├── genai_communication.py # Message generation
│   │   ├── ml_models.py      # ML implementations
│   │   ├── mock_data.py      # Demo data generators
│   │   ├── nlp_engine.py     # NLP processing
│   │   ├── rag_engine.py     # RAG system
│   │   ├── simulation_engine.py # Scenario planning
│   │   └── __init__.py
│   ├── main.py               # FastAPI app entry
│   └── __init__.py
├── dataset/                   # MIMIC-IV demo data
│   └── mimic-iv-clinical-database-demo-2.2/
├── .env                      # Environment variables
├── pyproject.toml           # Python dependencies
└── schema.sql               # Database schema
```

---

## 🖥️ Frontend Structure

```
web/
├── src/
│   ├── app/                  # Next.js pages
│   │   ├── agents/          # Agent workflow hub
│   │   ├── knowledge/       # RAG search interface
│   │   ├── patients/        # Patient management
│   │   ├── layout.tsx       # Root layout
│   │   └── page.tsx         # Dashboard
│   ├── components/           # React components
│   │   ├── agents/          # Agent-specific UI
│   │   │   ├── action-card.tsx
│   │   │   └── agent-state-stepper.tsx
│   │   ├── dashboard/       # Dashboard widgets
│   │   │   ├── alert-feed.tsx
│   │   │   ├── metric-card.tsx
│   │   │   └── prophet-chart.tsx
│   │   ├── layout/          # Layout components
│   │   │   ├── app-sidebar.tsx
│   │   │   └── page-transition.tsx
│   │   ├── patients/        # Patient UI
│   │   │   └── risk-badge.tsx
│   │   └── ui/              # Shared UI components
│   │       ├── button.tsx
│   │       ├── card.tsx
│   │       ├── dialog.tsx
│   │       ├── table.tsx
│   │       └── ... (18 total components)
│   ├── hooks/               # Custom hooks
│   │   └── use-mobile.ts
│   ├── lib/                 # Utilities
│   │   ├── api.ts          # Backend API client
│   │   ├── data-generators.ts
│   │   └── utils.ts
│   └── types/               # TypeScript types
├── public/                  # Static assets
├── package.json            # Dependencies
└── next.config.ts          # Next.js config
```

---

## 🏃 Getting Started

### Prerequisites
- Python 3.10+
- Node.js 18+
- PostgreSQL (Supabase account)
- Ollama (for LLM capabilities)

### Backend Setup

```bash
# Navigate to backend directory
cd backend

# Install dependencies
uv sync

# Set up environment variables
cp .env.example .env
# Edit .env with your Supabase credentials

# Run the backend
uv run python main.py
```

### Frontend Setup

```bash
# Navigate to web directory
cd web

# Install dependencies
npm install

# Run development server
npm run dev
```

### Access Points
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

---

## 📡 API Documentation

### Core Endpoints

**Forecasting**
```
GET /api/v1/forecasts/icu-occupancy
GET /api/v1/forecasts/er-arrivals
```

**Machine Learning**
```
GET /api/v1/ml/risk-scores/{patient_id}
GET /api/v1/ml/predictions/batch
```

**Time Series**
```
GET /api/v1/timeseries/forecast/{target}
GET /api/v1/timeseries/alerts
```

**Agents**
```
POST /api/v1/agents/run
POST /api/v1/agents/approve
```

**RAG**
```
POST /api/v1/rag/search
POST /api/v1/rag/documents
```

**Communication**
```
POST /api/v1/communication/simulate
```

---

## 🛣️ Development Roadmap

### Short Term (Current Focus)
- [ ] Complete Phase 3 frontend-backend integration
- [ ] Implement full human-in-the-loop workflow
- [ ] Add comprehensive testing suite
- [ ] Deploy to production environment

### Medium Term
- [ ] Integrate with real hospital EHR systems
- [ ] Expand ML models with deep learning approaches
- [ ] Add mobile-responsive interfaces
- [ ] Implement multi-hospital scaling

### Long Term Vision
- [ ] Federated learning across hospital networks
- [ ] Advanced predictive analytics with reinforcement learning
- [ ] Integration with IoT medical devices
- [ ] Real-time clinical decision support

---

## 🔒 Safety & Compliance

### Hallucination Prevention
- RAG-based grounding with similarity thresholds
- Guardrail agent validation
- Source citation enforcement
- Confidence scoring

### Audit & Transparency
- Full decision chain logging
- Human feedback integration
- Regulatory compliance (HIPAA, FDA considerations)
- Explainable AI principles

---

## 🤝 Contributing

This project welcomes contributions! Please see our contributing guidelines for:
- Code standards and practices
- Testing requirements
- Pull request process
- Issue reporting

---

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## 🙏 Acknowledgments

- **MIMIC-IV Database**: For providing the clinical dataset foundation
- **LangGraph Team**: For the agentic workflow framework
- **Open Source Community**: For the incredible tools and libraries

---

*## 📚 Detailed Technical Documentation

### Phase 2 Part 1: Core Architecture & Data Flow ("The Brain")

#### 1. High-Level Architecture Diagram

```mermaid
graph TD
    A[📂 MIMIC-IV Dataset CSVs] -->|Raw Data Streaming| B(⚙️ Time-Shift Replay Engine)
    B -->|Shifted to 2026| C{⚡ FastAPI Backend}
    
    subgraph "The Brain (Backend)"
    C -->|Store/Retrieve| D[(🗄️ Supabase Database)]
    C -->|Clean & Validate| E[🧩 Feature Store (Pydantic)]
    C -->|Calculate| F[📈 Forecasting Engine]
    end
    
    C -->|JSON API Response| G[💻 Frontend Dashboard]
```

#### 2. Detailed Implementation Breakdown

**1️⃣ Core Setup & Infrastructure**
- Framework: FastAPI + uv initialized
- Location: Project initialized on F:\ drive
- Role: Acts as the central nervous system handling all data requests

**2️⃣ Database Configuration ("The Memory")**
- System: Supabase (PostgreSQL)
- Function: Persists workflows, audit trails, and risk decisions
- Benefit: Turns the prototype into a system of record—data remains even if you refresh the page

**3️⃣ Data Ingestion: The Replay Engine ("The Heartbeat")**

This is the core innovation that simulates a live hospital environment using static data.

- Source: MIMIC-IV Clinical Database (CSVs)
- The Problem: Data is from years 2100-2200 (for anonymity)
- The Solution: Time-Shift Algorithm shifts dates to TODAY (2026)

| Original MIMIC Date | Time-Shift Offset | Frontend Display (What You See) |
|---------------------|-------------------|---------------------------------|
| 2125-03-15 08:00    | -99 Years         | 2026-01-19 08:00 (Today!)       |
| 2125-03-20 14:30    | -99 Years         | 2026-01-24 14:30                |

**4️⃣ Feature Store ("The Translator")**

- Logic: Uses Pydantic Models to clean messy raw data
- Process:
  - Input: Raw CSV code (e.g., I50.9)
  - Processing: Maps to readable clinical terms
  - Output: Frontend-ready JSON (e.g., "Heart Failure")

**5️⃣ Forecasting API Endpoints**

These endpoints power the live charts on the dashboard:

| Endpoint | Data Source | Frontend Visual |
|----------|-------------|-----------------|
| `/api/v1/forecasts/icu-occupancy` | icustays.csv + Circadian Algo | ICU Occupancy Chart (Live %) |
| `/api/v1/forecasts/er-arrivals` | Pattern Simulation | ER Arrivals Chart (Live Trend) |
| `/api/v1/patients` | patients.csv + admissions.csv | Patient List Table |

#### 3. Data Flow: From CSV to Dashboard

```
[SOURCE: icustays.csv]
       |
       v
[BACKEND: Replay Engine]
   -> Reads "intime": 2176-11-26
   -> Applies Offset: -150 years
   -> Result: "Current Occupancy" for 2026-01-19
       |
       v
[API: /api/v1/forecasts/icu-occupancy]
   -> Returns JSON: { "occupancy_rate": 88, "trend": "up" }
       |
       v
[FRONTEND: Control Tower Dashboard]
   -> Displays: "88% Occupancy" (Red Alert Badge 🔴)
```

Phase 2 Part 1 is COMPLETE. ✅

---

### Phase 2 Part 2: Machine Learning Engine 🧠

#### 1. What is it? (The "Clinical Brain")

Phase 2 Part 2 is the Intelligence Layer. While Part 1 (Replay Engine) provides the raw data (vitals, labs), Part 2 analyzes that data to predict future risks. It answers questions like:

- "Is this patient ready to go home?"
- "If we discharge them, will they bounce back (readmit) in 30 days?"
- "Is this stable patient about to crash (escalate)?"

#### 2. How it works from the Frontend 🖥️

When you open the application, here is the unseen flow of data:

**1. The Overview (Dashboard):**

- What you see: A list of active patients sorted by risk (Critical patients at the top)
- How it works: The frontend calls `GET /api/v1/ml/predictions/batch`
- Behind the scenes: The backend iterates through all active patients in the "Replay Engine", runs them through all 4 ML models instantly, sorts them by escalation_risk, and sends the JSON back

**2. The Detail View (Patient Profile):**

- What you see: Risk badges (e.g., "High Readmission Risk: 78%") and detailed contributing factors (e.g., "Factors: Age > 70, High Diagnosis Count")
- How it works: The frontend calls `GET /api/v1/ml/risk-scores/{patient_id}`
- Behind the scenes: The backend fetches that specific patient's live features and calculates fresh scores on the fly

#### 3. The 4 ML Models (Detailed Backend Logic) 🤖

I checked `backend/app/services/ml_models.py`. Here is exactly how each model "thinks":

**A. Discharge Readiness Model**

- Goal: Can this patient go home safely?
- Type: Simulates a Logistic Regression
- Logic:
  - Baseline: Starts at 60% (most people are getting better)
  - Positives (+): If they have stayed >3 days (treatment likely done)
  - Negatives (-): If they are currently in ICU (-20%), have sepsis (-15%), or are elderly (age factor)
- Result: A 0-100 score. >70% = "Ready"

**B. Readmission Risk Model**

- Goal: Will they return within 30 days?
- Type: Simulates a Gradient Boosting Classifier
- Logic:
  - Baseline: Starts at 15% (standard risk)
  - Risk Factors:
    - Diagnosis Count: If they have >5 complex diagnoses, risk jumps (+20%)
    - Comorbidities: Heart conditions (+25%) or Renal failure (+20%) are huge red flags
    - Age: >70 years old adds significant risk
- Result: A 0-100 score. >50% is High Risk

**C. Length of Stay (LOS) Predictor**

- Goal: How many days will they take up a bed?
- Type: Simulates a Linear Regression
- Logic:
  - Baseline: 3.0 days
  - Math:
    - +0.05 days for every year over age 50
    - +4.0 days if they are in ICU
    - +3.0 days if they have Sepsis
- Result: Returns a number of days (e.g., "Predicted LOS: 8.5 days")

**D. Escalation Risk Model (The "Watchdog") 🚨**

- Goal: Is a critical event imminent (next 24h)?
- Type: Simulates a Random Forest Classifier
- Logic:
  - Baseline: 15% (Low)
  - Critical Triggers:
    - Sepsis: Immediate +30% risk
    - ICU Status: +25% risk
    - Respiratory Issues: +15% risk
- Result: This score drives the "Monitor Agent". If this hits a threshold (e.g., >70%), it triggers the Agentic Workflow automatically

#### Summary

Phase 2 Part 2 acts as the Data Scientist of the team. It takes raw charts and turns them into actionable probabilities that the Frontend displays as clean, color-coded badges. This allows the Agents (Phase 2 Part 6) to know when to wake up and start working.

---

### Phase 2 Part 3: Time Series Analysis (Operational Forecasting) 📈

#### 1. What is it? (The "Crystal Ball") 🔮

Phase 2 Part 3 is the Forecasting Layer. While the ML Engine (Part 2) looks at individual patients, this component looks at the entire hospital. It processes historical data to predict Operational Bottlenecks before they happen.

- "Will the ER be overwhelmed at 6 PM tonight?"
- "Will we run out of ICU beds by Thursday?"

#### 2. How it works from the Frontend 🖥️

When you look at the Dashboard charts, here is the flow:

**1. The Live Charts (Prophet Viz):**

- What you see: A line chart showing past data (solid line), future predictions (dotted line), and a shaded area (Confidence Interval)
- How it works: The Frontend calls `GET /api/v1/timeseries/forecast/icu_occupancy`
- Behind the scenes: The Backend calculates the trend + seasonality, and returns a 24-hour forecast. The "shaded area" represents the uncertainty (the backend calls this lower_bound and upper_bound)

**2. Real-Time Alerts:**

- What you see: A flashing red alert "Critical: ICU Capacity > 90% Predicted"
- How it works: The Frontend calls `GET /api/v1/timeseries/alerts`
- Behind the scenes: The TimeSeriesForecaster runs a check on every forecast. If a predicted value crosses the 90% threshold (THRESHOLDS config), it creates a RiskEvent

#### 3. The Backend Logic (`forecasting_engine.py`) ⚙️

I analyzed the code in `backend/app/services/forecasting_engine.py`. It uses a sophisticated statistical approach known as ARIMA + Decomposition. Here is the step-by-step math it performs:

**A. Data Generation (`_generate_historical_data`)**

Since this is a demo system without 10 years of real hospital logs, this function generates realistic synthetic data based on real clinical patterns (MIMIC-IV):

- ICU Occupancy: Peaks mid-week (Surgeries happen Mon-Wed), drops on weekends
- ER Arrivals: Peaks in the evening (6 PM - 10 PM), surges on weekends
- Ward Occupancy: Slow, gradual changes over days

**B. The 'Seasonality Decomposition' (`_decompose_seasonality`)**

The engine is smart enough to understand time. It breaks the data into 3 parts:

- Trend: Is the hospital getting busier or quieter overall? (The average)
- Daily Pattern (24h): It calculates the average deviation for every hour of the day. (e.g., "At 3 AM, we are usually 10% quieter")
- Weekly Pattern (7d): It calculates the average deviation for every day of the week. (e.g., "Fridays are 5% busier")

**C. The Prediction Logic (`forecast` function)**

To predict the future (e.g., "What will happen 4 hours from now?"), it combines these layers:

"Prediction = (Average) + (What happened recently * AR Factor) + (Daily Pattern for that hour) + (Weekly Pattern for that day)"

**D. Threshold Logic (`check_thresholds`)**

It constantly monitors these 3 critical metrics:

- ICU Occupancy: Critical if >90% (Code Red)
- ER Arrivals: Critical if >25 patients/hour (Overwhelmed)
- Ward Occupancy: Critical if >95% (Bed Block)

#### Summary

Phase 2 Part 3 acts as the Hospital Meteorologist. Instead of predicting rain, it predicts patient surges.

- Frontend: Displays the "Weather Forecast" (Charts) and "Storm Warnings" (Alerts)
- Backend: Uses math (ARIMA/Seasonality) to look at the past 30 days and mathematically project the next 24 hours

This allows the Monitor Agent (Part 6) to "see the future" and warn the staff before the hospital runs out of beds.

---

### Phase 2 Part 4: NLP Pipeline

#### Why NLP in This Project? 🏥

**The Problem:**
Hospitals have thousands of clinical notes every day - handwritten by doctors, nurses, specialists. These notes contain:
- Patient symptoms
- Medications prescribed
- Vital signs
- Diagnoses

But this data is unstructured text - computers can't easily analyze it.

#### How NLP Helps ACCT:

**1️⃣ Feeding the AI Agents**

```
Clinical Note → NLP extracts entities → AI Agent can understand
                    ↓
        "Patient has sepsis, on Vancomycin"
                    ↓
        Agent triggers alert: "High-risk patient!"
```

**2️⃣ Building the Knowledge Base (RAG)**

```
1000s of protocols/notes → NLP de-identifies PHI
                    ↓
        Safe to store in vector DB
                    ↓
        AI can search & retrieve
```

**3️⃣ Risk Prediction**

```
Patient note mentions: "diabetic, chest pain, elevated troponin"
                    ↓
        NLP extracts: DISEASE, VITAL_SIGN, LAB_VALUE
                    ↓
        ML model predicts: "High cardiac event risk"
```

#### ACCT Architecture with NLP:

```
___________________________________________________________
|                  ACCT Control Tower                     |
|_________________________________________________________|
|                                                         |
|  Clinical Notes ─→ NLP Pipeline ─→ Extracted Entities   |
|        |                |                  |            |
|        |                |                  ▼            |
|        |                |           Risk Prediction     |
|        |                |           Agent Actions       |
|        |                ▼                               |
|        |        De-identified Text                      |
|        |                |                               |
|        |                ▼                               |
|        |        RAG Knowledge Base                      |
|        |                |                               |
|        └────────────────┴─→ AI Agents make decisions    |
|                                                         |
|_________________________________________________________|
```

#### In Simple Terms:

| Without NLP | With NLP |
|-------------|----------|
| AI can't read doctor's notes | AI understands medical terms |
| Can't auto-detect high-risk drugs | Alerts if dangerous drug combo |
| PHI exposed in data | PHI safely removed |
| Manual protocol lookup | AI searches knowledge base |

NLP is the "translator" between human medical text and AI systems!

---

### Phase 2 Part 5: RAG Pipeline

#### How RAG Search Works

When you searched "patient", here's exactly what happened:

```
               YOU TYPE: "patient"
                        |
                        ▼
____________________________________________________
| STEP 1: EMBED YOUR QUERY                         |
| ________________________________________         |
|                                                  |
| Your text "patient" is converted to a            |
| 384-dimensional vector using the                 |
| all-MiniLM-L6-v2 model                           |
|                                                  |
| "patient" -> [0.123, -0.456, 0.789, ... 384 nums]|
|__________________________________________________|
                        |
                        ▼
____________________________________________________
| STEP 2: COMPARE TO ALL DOCUMENT CHUNKS           |
| ________________________________________         |
|                                                  |
| The knowledge base has 3 documents split into    |
| 9 chunks. Each chunk was pre-embedded when added.|
|                                                  |
| Calculate cosine similarity between YOUR vector  |
| and EACH chunk:                                  |
|                                                  |
| Chunk 1 ("Home care services...") -> 49% similar |
| Chunk 2 ("Teach-back method...")  -> 47% similar |
| Chunk 3 ("Consider transfer...")  -> 44% similar |
| Chunk 4 ("Vasopressors...")       -> 38% similar |
|__________________________________________________|
                        |
                        ▼
____________________________________________________
| STEP 3: RETURN TOP K RESULTS (sorted by relevance)|
| ________________________________________          |
|                                                   |
| Frontend displays the chunks with highest         |
| similarity scores                                 |
|___________________________________________________|
```

#### What's in the Knowledge Base?

The backend has 3 documents pre-loaded:

| Document | Type | Content |
|----------|------|---------|
| ICU Capacity Management SOP | SOP | Surge protocols, transfer guidelines |
| Sepsis Management Guidelines | Guideline | Vasopressors, bundle completion |
| Discharge Planning Guidelines | SOP | Patient education, follow-up |

Each document is chunked into ~200-500 character pieces (9 total chunks) so the search can find specific relevant sections.

#### Why RAG is Powerful for ACCT

| Without RAG | With RAG |
|-------------|----------|
| AI makes up answers (hallucination) | AI retrieves from verified sources |
| No citations | Returns exact document chunks |
| Generic responses | Hospital-specific SOPs |

**RAG = AI doesn't guess. It looks up the answer first, then responds!**

#### Why Do I Need This?

**Real-World Problem: AI Agents Need Reliable Information**

**Scenario Without RAG:**

Nurse asks AI: "What's the ICU surge protocol?"

AI (without RAG): "Generally, you should... [makes up generic answer]"

❌ Could be WRONG
❌ Not your hospital's specific protocol
❌ Potentially dangerous advice

**Scenario With RAG:**

Nurse asks AI: "What's the ICU surge protocol?"

AI (with RAG):
- Searches knowledge base → Finds "ICU Capacity Management SOP"
- Returns EXACT text from your hospital's document
- Shows citation: "Source: Hospital Policy Manual v2.3"

✅ ACCURATE - from verified document
✅ TRACEABLE - you know where it came from
✅ SAFE - hospital-approved protocols

#### Why ACCT Needs RAG:

| Component | How It Uses RAG |
|-----------|-----------------|
| AI Agents | Look up protocols before recommending actions |
| Planning Agent | Finds discharge guidelines before creating plan |
| Guardrail Agent | Verifies actions against hospital policies |
| Nurses/Physicians | Search SOPs instantly instead of reading 100-page PDFs |

#### The Key Benefit: Trust

```
_______________________________________________________
|                                                     |
| Without RAG: AI answers = "Trust me, bro"           |
|                      |                              |
| With RAG:    AI answers = "According to your        |
|              ICU Capacity Management SOP,           |
|              section 3.2, the protocol is..."       |
|                      |                              |
|              [Shows source, page, relevance]        |
|_____________________________________________________|
```

In healthcare, you can't afford AI that guesses. RAG ensures every recommendation is backed by YOUR hospital's verified documents.

#### What You're Doing Now vs. What AI Agents Will Do

**Current UI (What you're doing):**

```
YOU manually type "patient" -> Search -> See results
                    ↓
        This is just a DIRECT SEARCH tool for humans
        (Like Google for your hospital documents)
```

This is useful for: Nurses/doctors who want to quickly find a protocol instead of reading 100-page PDFs.

**The Two Use Cases:**

| Use Case | Who Uses It | How |
|----------|-------------|-----|
| Manual Search (what you just did) | Humans | Type in search bar, read results |
| Agent-Powered RAG (Part 6) | AI Agents | Automatically fetch when agent runs |

#### In Part 6 (Agents), It Will Work Like This:

```
User: "Create a discharge plan for patient P-001"
              |
              ▼
_____________________________________________________
|                                                   |
| PLANNING AGENT                                    |
|                                                   |
| 1. Check patient data (from /patients API)        |
| 2. ⭐ SEARCH RAG: "discharge planning guidelines" | ← THIS is where RAG matters!
| 3. Use the retrieved protocol to CREATE plan      |
| 4. Return plan WITH CITATIONS                     |
|___________________________________________________|
              |
              ▼
"Based on Discharge Planning Guidelines (section 2.3),
patient should receive follow-up call within 48 hours..."
```

#### TL;DR:

| What | Purpose |
|------|---------|
| The search bar you used | Human convenience |
| RAG in AI Agents (Part 6) | AI looks things up AUTOMATICALLY before giving advice |

The search UI is a bonus. The real value is when AI agents use RAG automatically in Part 6!

#### Where Do These Documents Come From?

Great question! You're right - you didn't give me any documents. These are pre-seeded sample documents built into the backend for demo purposes.

The documents are auto-generated when the backend starts in the RAG engine. Let me show you:

`backend/app/services/rag_engine.py`

When `get_rag_engine()` is called, it creates sample documents:

| Document | Purpose |
|----------|---------|
| ICU Capacity Management SOP | Sample hospital protocol for ICU surge |
| Sepsis Bundle Protocol | Sample clinical guideline for sepsis treatment |
| Discharge Planning Guidelines | Sample discharge protocol |

**Why Are They There?**

- Demo purposes - So the system works out of the box without you uploading anything
- Testing RAG - So searches return results immediately
- AI Agent context - So agents have documents to reference

**In a Real Hospital:**

You would:
- Upload YOUR hospital's actual SOPs and protocols
- Use the API: `POST /api/v1/rag/documents` with your content
- Remove or replace the sample documents

**To Add Your Own Documents:**

```bash
# Using the API:
POST http://localhost:8000/api/v1/rag/documents
{
    "title": "Your Protocol Name",
    "content": "The full text of your document...",
    "source": "Hospital Name - Department",
    "doc_type": "sop" // or "guideline", "policy"
}
```

These are just placeholder data for demonstration - like the sample patient data in MIMIC-IV!

---

### Phase 2 Part 6: Agentic AI Workflow

#### How the Agent Hub Workflow Works - Complete Breakdown

When you click "Run Workflow", here's exactly what happens:

#### The 5-Agent Pipeline

```
____________________________________________________
|                                                  |
|           YOU CLICK "Run Workflow"               |
|              Target Role: Nurse                  |
|__________________________________________________|
                        |
                        ▼
____________________________________________________
| AGENT 1: MONITOR AGENT 📊                        |
| ________________________                         |
|                                                  |
| Job: Continuously checks for risk events         |
|                                                  |
| What it does:                                    |
| • Checks ICU occupancy forecast (is it > 85%?)   |
| • Checks ER arrival predictions                  |
| • Checks patient vitals for anomalies            |
|                                                  |
| OUTPUT: "icu_occupancy_warning" detected!        |
|         Severity: HIGH                           |
|__________________________________________________|
                    |
                    ▼
____________________________________________________
| AGENT 2: RETRIEVAL AGENT 📚                      |
| __________________________                       |
|                                                  |
| Job: Search RAG Knowledge Base for relevant      |
|      protocols                                   |
|                                                  |
| What it does:                                    |
| • Takes the risk event: "ICU occupancy warning"  |
| • Searches knowledge base using embeddings       |
| • Finds: "ICU Capacity Management SOP"           |
|                                                  |
| OUTPUT: Retrieved document chunks with 71%       |
|         relevance match                          |
|         Source: "Hospital Policy Manual v2.3"    |
|__________________________________________________|
                    |
                    ▼
____________________________________________________
| AGENT 3: PLANNING AGENT 🤖 (LLM-Powered)         |
| __________________________                       |
|                                                  |
| Job: Generate an ActionCard with specific steps  |
|                                                  |
| What it does:                                    |
| • Takes: Risk event + Retrieved SOP context      |
| • Sends to Ollama LLM (llama3.2:1b)              |
| • LLM generates structured action plan           |
|                                                  |
| OUTPUT: ActionCard                               |
| {                                                |
|   "title": "Transfer Patients Due to High ICU    |
|             Occupancy Warning",                  |
|   "steps": [                                     |
|     "Contact charge nurse to assess              |
|      discharge-ready patients",                  |
|     "Notify attending physician and prepare      |
|      step-down beds",                            |
|     "Activate ICU surge protocol"                |
|   ],                                             |
|   "cited_sources": ["ICU Capacity Management     |
|                      SOP"]                       |
| }                                                |
|__________________________________________________|
                    |
                    ▼
____________________________________________________
| AGENT 4: GUARDRAIL AGENT ✓                       |
| ___________________________                      |
|                                                  |
| Job: Validate the LLM's plan is SAFE             |
|                                                  |
| What it checks:                                  |
| • Does the plan comply with hospital policies?   |
| • Are there any dangerous recommendations?       |
| • Does it cite valid sources?                    |
| • Is the plan within approved action types?      |
|                                                  |
| OUTPUT: validation_passed = TRUE ✓               |
|         (shown as "✓ Validated")                 |
|__________________________________________________|
                    |
                    ▼
____________________________________________________
| AGENT 5: NOTIFIER AGENT 💬                       |
| __________________________                       |
|                                                  |
| Job: Format the ActionCard for the target role   |
|      (Nurse)                                     |
|                                                  |
| What it does:                                    |
| • Takes the validated ActionCard                 |
| • Formats specifically for "nurse" role (not     |
|   physician/admin)                               |
| • Adds priority level, task checklist, delivery  |
|   timestamp                                      |
|                                                  |
| OUTPUT:                                          |
| "ACTION REQUIRED: Transfer Patients Due to High  |
|  ICU Occupancy Warning                           |
|  Priority: HIGH                                  |
|  Task List:                                      |
|  ⬜ Contact charge nurse to assess which         |
|     patients need transfer                       |
|  ⬜ Notify attending physician and prepare       |
|     step-down beds                               |
|  ⬜ Activate ICU surge protocol"                 |
|__________________________________________________|
```

#### Your Screenshots Explained

**Image 1 - Risk Detection & Action Card:**

| Component | What It Means |
|-----------|---------------|
| Workflow ID | Unique identifier for this run |
| ✓ Validated | Guardrail Agent approved the plan as safe |
| icu_occupancy_warning | Monitor Agent detected ICU is getting full |
| Severity: high | This is an urgent issue |
| 📚 ICU Capacity Management SOP | Retrieved from RAG Knowledge Base |

**Image 2 - Formatted Message for Nurse:**

| Component | What It Means |
|-----------|---------------|
| Message for nurse | Notifier Agent formatted this for nurses |
| Priority: HIGH | Urgency level based on severity |
| Task List | Actionable checklist generated by Planning Agent |
| Delivery timestamp | When the message was created |

**Image 3 - Agent Execution History:**

```
1. monitor -> 2. retrieval -> 3. planning -> 4. guardrail -> 5. notifier
```

This shows the exact order agents ran!

#### Why This Matters for Hospitals

| Without Agentic AI | With ACCT Agents |
|--------------------|------------------|
| Nurse manually checks dashboards | Monitor Agent watches 24/7 |
| Nurse searches for SOP in binder | Retrieval Agent finds SOP in 0.5s |
| Nurse decides what to do | Planning Agent suggests validated steps |
| No safety check | Guardrail Agent prevents dangerous actions |
| Same message for everyone | Notifier formats per role |

#### Why You Need Agent Workflows - The Real Problem

**The Problem in Hospitals Today:**

```
_________________________________________________________
|                                                       |
| SCENARIO: ICU is 92% full at 2 AM                     |
|_______________________________________________________|
|                                                       |
| WITHOUT ACCT:                                         |
| _____________                                         |
|                                                       |
| • Night nurse doesn't notice dashboard warning        |
| • At 5 AM, ER sends 2 more patients -> ICU is 100%    |
|   full                                                |
| • Chaos: No beds, patients waiting, ambulances        |
|   diverted                                            |
| • Nurse scrambles to find SOP -> takes 15 mins        |
| • Makes decisions under stress -> potential mistakes  |
|                                                       |
| RESULT: ❌ Patient care delayed, staff overwhelmed    |
|_______________________________________________________|
|                                                       |
| WITH ACCT AGENTS:                                     |
| _________________                                     |
|                                                       |
| • Monitor Agent detects warning at 2 AM automatically |
| • Retrieval Agent instantly finds ICU Surge Protocol  |
| • Planning Agent generates step-by-step action plan   |
| • Guardrail validates it's safe                       |
| • Notifier sends ALERT to night nurse's dashboard     |
|                                                       |
| "ACTION: Transfer P-1025 to Ward B. Contact Dr.       |
|  Smith."                                              |
|                                                       |
| RESULT: ✅ Crisis prevented BEFORE it happens         |
|_______________________________________________________|
```

#### The Key Benefits

| Feature | Why It Matters |
|---------|----------------|
| 24/7 Monitoring | Humans miss things. Agents don't sleep |
| Instant SOP Lookup | No more searching through PDFs |
| Validated Actions | Guardrail prevents dangerous suggestions |
| Role-Specific | Nurse gets nurse-relevant tasks, not admin stuff |
| Audit Trail | Every decision logged for compliance |

#### Real Use Cases:

- **ICU Surge** - Transfer patients before overflow
- **Sepsis Detection** - Alert on vitals pattern → order sepsis bundle
- **Discharge Planning** - Identify patients ready to go home
- **Staffing Crisis** - Predict shortage → call backup staff
- **Equipment Failure** - Detect anomaly → alert biomedical team

---

### Phase 2 Part 7: Generative AI Communication Layer

#### What is "AI Scenario Simulation"?

This feature allows hospital administrators to ask "What-If" questions and get AI-powered predictions about operational impacts.

#### Real-World Use Cases:

| Scenario You Type | What AI Predicts |
|-------------------|------------------|
| "ER surge of 50% more patients in 2 hours" | Risk level, bed reallocation needs, staffing increases |
| "ICU at 100% capacity tomorrow due to flu outbreak" | Cascade effects on other units, transfer protocols |
| "2 nurses call in sick for night shift" | Coverage gaps, patient safety risks, solutions |
| "Power outage affecting east wing for 4 hours" | Equipment impact, patient relocation needs |

#### Why is this Useful?

- **Proactive Planning**: Instead of reacting to crises, administrators can prepare in advance
- **Resource Optimization**: Predicts what beds, staff, or equipment will be needed
- **Decision Support**: Gives concrete recommendations (not just guesses) based on the LLM's understanding of hospital operations
- **Training Tool**: New staff can explore "what would happen if..." scenarios safely

#### How it Works (Backend)

```
User Input -> /api/v1/communication/simulate -> LLM (Ollama) -> Structured JSON Response
```

The backend sends your scenario to the Ollama LLM, which generates:

- Predicted Impact (what will likely happen)
- Risk Level (low/medium/high/critical)
- Recommended Preparations (actionable steps)

In short: This turns your Control Tower from a monitoring dashboard into a predictive planning tool powered by AI.

#### What Was Implemented

- **Scenario Simulation Dialog**: Opens when clicking "Simulate Scenario" on the Dashboard
- **Backend Integration**: Calls `/api/v1/communication/simulate` with user input
- **AI Response Display**: Shows:
  - Risk Level: (e.g., "high")
  - Predicted Impact: (e.g., "ER surge leads to increased demand for hospital services")
  - Recommended Preparations: (e.g., "Implement temporary surge planning", "Reallocate ICU beds", "Increase staffing")

#### Verified by Browser Test:

✅ Dialog opens correctly
✅ Input accepts scenario description
✅ Backend returns AI-generated predictions
✅ Results display with risk color coding

---

### Phase 2 Part 8: Evaluation & Safety (Trust Layer)

This layer ensures the AI is safe, accurate, and auditable before it is used in a clinical setting.

#### 1. Hallucination Control Layers

**RAG Layer**: Enforces confident retrieval using RAGEngine thresholds.

- What this means: If the AI cannot find a document with high similarity (e.g., >75% match), it will not answer rather than guessing

**Agentic Layer**: The Guardrail Agent validates Planner outputs.

- What this means: Before any plan is shown to a nurse/doctor, a specific "Safety Agent" reviews it to ensure it follows hospital rules

#### 2. Evaluation Metrics Framework

**ML/RAG/Agent Tracking**: The EvaluationService logs performance metrics.

- What this means: The system records how accurate the Machine Learning models are and how often the RAG system finds the right document

**Auto-Logging**: The Orchestrator automatically logs:

- Retrieval Success: Did we find the right SOP?
- Workflow Completion: Did the agents finish the task successfully?

#### 3. Human-in-the-Loop (HITL)

**Feedback Loop**: Implements the `/evaluation/feedback` endpoint.

- What this means: Allows users (Doctors/Nurses) to click "Thumbs Up/Down" on AI recommendations. This data is saved to improve the model

**Audit Trail**: Implements the `/evaluation/audit` endpoint.

- What this means: The system can reconstruct the full decision history (Monitor -> Retrieval -> Planning -> Guardrail) so administrators can see exactly why the AI made a specific recommendation

#### Why This is Important for a Hospital System:

- **Quality Assurance**: Administrators can review if AI recommendations are clinically appropriate
- **Continuous Improvement**: Negative feedback helps identify what needs to be fixed
- **Audit Compliance**: Healthcare requires audit trails for any AI-assisted decisions (for regulatory bodies like FDA, HIPAA)
- **Trust Building**: Users see why the AI made a decision, not just what it decided

---

"Transforming healthcare from reactive to proactive, one prediction at a time."*