-- ACCT Database Schema for Supabase
-- Run this SQL in Supabase SQL Editor

-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Workflows table (stores agent workflow results)
CREATE TABLE IF NOT EXISTS workflows (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workflow_id TEXT UNIQUE NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending',
    trigger_type TEXT DEFAULT 'auto',
    target_role TEXT DEFAULT 'nurse',
    risk_event JSONB,
    action_card JSONB,
    final_output JSONB,
    agent_history JSONB DEFAULT '[]',
    validation_passed BOOLEAN DEFAULT false,
    validation_errors JSONB DEFAULT '[]',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ
);

-- Feedback table (thumbs up/down from users)
CREATE TABLE IF NOT EXISTS feedback (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workflow_id TEXT NOT NULL,
    feedback_type TEXT NOT NULL,
    comments TEXT,
    user_role TEXT DEFAULT 'unknown',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Metrics table (ML/RAG/Agent performance)
CREATE TABLE IF NOT EXISTS metrics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    category TEXT NOT NULL,
    metric_name TEXT NOT NULL,
    value FLOAT NOT NULL,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Audit Events table (full decision history)
CREATE TABLE IF NOT EXISTS audit_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workflow_id TEXT NOT NULL,
    agent TEXT NOT NULL,
    action TEXT,
    details JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Documents table (RAG knowledge base)
CREATE TABLE IF NOT EXISTS documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    doc_id TEXT UNIQUE NOT NULL,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Document chunks with embeddings (for vector search)
CREATE TABLE IF NOT EXISTS doc_embeddings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    doc_id TEXT NOT NULL,
    chunk_index INT NOT NULL,
    chunk_text TEXT NOT NULL,
    embedding VECTOR(384),
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_workflows_status ON workflows(status);
CREATE INDEX IF NOT EXISTS idx_workflows_created ON workflows(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_feedback_workflow ON feedback(workflow_id);
CREATE INDEX IF NOT EXISTS idx_metrics_category ON metrics(category);
CREATE INDEX IF NOT EXISTS idx_audit_workflow ON audit_events(workflow_id);
CREATE INDEX IF NOT EXISTS idx_doc_embeddings_doc ON doc_embeddings(doc_id);

-- Grant access to anon role (for API access)
GRANT ALL ON workflows TO anon;
GRANT ALL ON feedback TO anon;
GRANT ALL ON metrics TO anon;
GRANT ALL ON audit_events TO anon;
GRANT ALL ON documents TO anon;
GRANT ALL ON doc_embeddings TO anon;
