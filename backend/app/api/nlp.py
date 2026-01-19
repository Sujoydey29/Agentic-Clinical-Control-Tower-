"""
API Routes - NLP endpoint.
Provides clinical text processing, PHI de-identification, and NER.
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List, Optional

from ..services.nlp_engine import get_nlp_pipeline

router = APIRouter(prefix="/nlp", tags=["NLP Pipeline"])


class TextInput(BaseModel):
    """Input model for text processing."""
    text: str
    include_entities: bool = True
    include_summary: bool = False


class BatchTextInput(BaseModel):
    """Input model for batch text processing."""
    texts: List[str]


@router.post("/process")
async def process_clinical_text(input_data: TextInput) -> Dict[str, Any]:
    """
    Process clinical text through the full NLP pipeline.
    
    Steps:
    1. De-identify PHI (names, dates, MRN, etc.)
    2. Extract clinical entities (diseases, drugs, procedures)
    3. Prepare for RAG embedding
    
    Returns processed text with entities and metadata.
    """
    if not input_data.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty")
    
    pipeline = get_nlp_pipeline()
    result = pipeline.process_clinical_note(input_data.text)
    
    if input_data.include_summary:
        result["clinical_summary"] = pipeline.summarize_entities(input_data.text)
    
    return result


@router.post("/deidentify")
async def deidentify_text(input_data: TextInput) -> Dict[str, Any]:
    """
    Remove Protected Health Information (PHI) from text.
    
    Detects and redacts:
    - Names (Dr., Mr., Mrs., etc.)
    - Dates (various formats)
    - MRN/Patient IDs
    - SSN, Phone, Email
    - Age mentions
    
    Returns de-identified text with list of redactions made.
    """
    if not input_data.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty")
    
    pipeline = get_nlp_pipeline()
    deid_text, phi_matches = pipeline.deidentify(input_data.text)
    
    return {
        "original_text": input_data.text,
        "deidentified_text": deid_text,
        "phi_found": [
            {
                "text": m.text,
                "type": m.phi_type.value,
                "replacement": m.replacement,
                "position": {"start": m.start, "end": m.end},
            }
            for m in phi_matches
        ],
        "phi_count": len(phi_matches),
    }


@router.post("/extract-entities")
async def extract_entities(input_data: TextInput) -> Dict[str, Any]:
    """
    Extract clinical entities from text.
    
    Entity types:
    - DISEASE: Medical conditions
    - DRUG: Medications
    - PROCEDURE: Medical procedures
    - ANATOMY: Body parts
    - VITAL_SIGN: Blood pressure, heart rate, etc.
    - LAB_VALUE: Lab results
    
    Returns entities with positions and labels.
    """
    if not input_data.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty")
    
    pipeline = get_nlp_pipeline()
    entities = pipeline.extract_entities(input_data.text)
    
    # Group by type
    by_type = {}
    for entity in entities:
        if entity.label not in by_type:
            by_type[entity.label] = []
        by_type[entity.label].append({
            "text": entity.text,
            "start": entity.start,
            "end": entity.end,
        })
    
    return {
        "text": input_data.text,
        "entities": [
            {"text": e.text, "label": e.label, "start": e.start, "end": e.end}
            for e in entities
        ],
        "entities_by_type": by_type,
        "entity_count": len(entities),
    }


@router.post("/summarize")
async def summarize_text(input_data: TextInput) -> Dict[str, Any]:
    """
    Generate a clinical summary of the text.
    
    Extracts key clinical information and organizes by category.
    """
    if not input_data.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty")
    
    pipeline = get_nlp_pipeline()
    summary = pipeline.summarize_entities(input_data.text)
    
    return {
        "original_text": input_data.text,
        "summary": summary,
    }


@router.post("/prepare-for-embedding")
async def prepare_for_embedding(input_data: TextInput) -> Dict[str, Any]:
    """
    Prepare text for RAG embedding.
    
    Steps:
    1. De-identify PHI
    2. Normalize whitespace
    3. Clean punctuation
    
    Returns embedding-ready text.
    """
    if not input_data.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty")
    
    pipeline = get_nlp_pipeline()
    result = pipeline.process_clinical_note(input_data.text)
    
    return {
        "original_text": input_data.text,
        "embedding_ready_text": result["embedding_ready_text"],
        "phi_removed_count": result["phi_count"],
        "entity_count": result["entity_count"],
    }


@router.get("/entity-types")
async def list_entity_types() -> Dict[str, Any]:
    """
    List supported clinical entity types.
    """
    from ..services.nlp_engine import EntityType
    
    return {
        "entity_types": [
            {"name": "DISEASE", "description": "Medical conditions and diagnoses"},
            {"name": "DRUG", "description": "Medications and pharmaceuticals"},
            {"name": "PROCEDURE", "description": "Medical procedures and interventions"},
            {"name": "ANATOMY", "description": "Body parts and anatomical structures"},
            {"name": "VITAL_SIGN", "description": "Vital sign measurements"},
            {"name": "LAB_VALUE", "description": "Laboratory test results"},
        ]
    }


@router.get("/phi-types")
async def list_phi_types() -> Dict[str, Any]:
    """
    List supported PHI types for de-identification.
    """
    from ..services.nlp_engine import PHIType
    
    return {
        "phi_types": [
            {"name": "NAME", "description": "Patient or provider names"},
            {"name": "DATE", "description": "Dates in various formats"},
            {"name": "MRN", "description": "Medical Record Numbers"},
            {"name": "SSN", "description": "Social Security Numbers"},
            {"name": "PHONE", "description": "Phone numbers"},
            {"name": "EMAIL", "description": "Email addresses"},
            {"name": "AGE", "description": "Age mentions"},
        ]
    }


@router.get("/status")
async def nlp_status() -> Dict[str, Any]:
    """Get NLP engine status."""
    return {
        "status": "operational",
        "engine": "Regex-based NER + PHI Detection",
        "features": {
            "phi_deidentification": True,
            "clinical_ner": True,
            "entity_extraction": True,
            "text_summarization": True,
            "embedding_preparation": True,
        },
        "supported_phi_types": 7,
        "supported_entity_types": 6,
    }
