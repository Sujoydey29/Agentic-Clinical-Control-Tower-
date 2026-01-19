"""
NLP Pipeline - Clinical Text Processing

Implements NLP capabilities for clinical text:
- PHI De-identification (remove names, dates, IDs)
- Clinical NER (extract diseases, drugs, procedures)
- Text Summarization (via LLM integration)
- Text-to-Structure conversion

Uses spaCy for NER and regex patterns for PHI detection.
"""
import re
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
from datetime import datetime


class EntityType(str, Enum):
    """Clinical entity types."""
    DISEASE = "DISEASE"
    DRUG = "DRUG"
    PROCEDURE = "PROCEDURE"
    ANATOMY = "ANATOMY"
    LAB_VALUE = "LAB_VALUE"
    VITAL_SIGN = "VITAL_SIGN"


class PHIType(str, Enum):
    """Protected Health Information types."""
    NAME = "NAME"
    DATE = "DATE"
    MRN = "MRN"
    SSN = "SSN"
    PHONE = "PHONE"
    EMAIL = "EMAIL"
    ADDRESS = "ADDRESS"
    AGE = "AGE"


@dataclass
class Entity:
    """Extracted clinical entity."""
    text: str
    label: str
    start: int
    end: int
    confidence: float = 1.0


@dataclass
class PHIMatch:
    """PHI detection result."""
    text: str
    phi_type: PHIType
    start: int
    end: int
    replacement: str


class ClinicalNLPPipeline:
    """
    Clinical NLP processing pipeline.
    
    Features:
    - PHI De-identification using regex patterns
    - Clinical Named Entity Recognition
    - Text summarization preparation
    """
    
    # PHI Detection Patterns
    PHI_PATTERNS = {
        PHIType.NAME: [
            r'\b(?:Dr\.?|Mr\.?|Mrs\.?|Ms\.?)\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)?',
            r'\b[A-Z][a-z]+\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)?\b',
        ],
        PHIType.DATE: [
            r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b',
            r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{1,2},?\s+\d{4}\b',
            r'\b\d{4}-\d{2}-\d{2}\b',
        ],
        PHIType.MRN: [
            r'\bMRN[:\s]*\d{6,10}\b',
            r'\b(?:Patient\s+ID|PID)[:\s]*\d+\b',
        ],
        PHIType.SSN: [
            r'\b\d{3}-\d{2}-\d{4}\b',
        ],
        PHIType.PHONE: [
            r'\b\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b',
        ],
        PHIType.EMAIL: [
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
        ],
        PHIType.AGE: [
            r'\b\d{1,3}\s*(?:year|yr|y\.?o\.?|years?\s*old)\b',
        ],
    }
    
    # Clinical Entity Patterns (simplified - would use spaCy/MedSpaCy in production)
    CLINICAL_PATTERNS = {
        EntityType.DISEASE: [
            r'\b(?:diabetes|hypertension|CHF|heart failure|pneumonia|sepsis|COPD|'
            r'asthma|stroke|MI|myocardial infarction|cancer|infection|fever|'
            r'arrhythmia|atrial fibrillation|kidney disease|renal failure|'
            r'respiratory failure|anemia|depression|anxiety)\b',
        ],
        EntityType.DRUG: [
            r'\b(?:aspirin|metformin|lisinopril|metoprolol|atorvastatin|'
            r'omeprazole|amlodipine|albuterol|prednisone|gabapentin|'
            r'losartan|furosemide|hydrochlorothiazide|insulin|heparin|'
            r'warfarin|clopidogrel|acetaminophen|ibuprofen|morphine)\b',
        ],
        EntityType.PROCEDURE: [
            r'\b(?:surgery|catheterization|intubation|dialysis|biopsy|'
            r'MRI|CT scan|X-ray|ultrasound|EKG|ECG|echocardiogram|'
            r'colonoscopy|endoscopy|bronchoscopy|angioplasty|CABG|'
            r'tracheostomy|thoracentesis|lumbar puncture)\b',
        ],
        EntityType.ANATOMY: [
            r'\b(?:heart|lung|liver|kidney|brain|chest|abdomen|'
            r'left ventricular|right ventricular|pulmonary|hepatic|renal|'
            r'cardiac|coronary|aortic|mitral|tricuspid)\b',
        ],
        EntityType.VITAL_SIGN: [
            r'\b(?:BP|blood pressure|HR|heart rate|RR|respiratory rate|'
            r'SpO2|O2 sat|oxygen saturation|temp|temperature|pulse)\s*'
            r'(?:of\s+)?[\d./]+(?:\s*(?:mmHg|bpm|/min|%|°[CF]))?',
        ],
        EntityType.LAB_VALUE: [
            r'\b(?:WBC|RBC|Hgb|Hct|platelets?|creatinine|BUN|glucose|'
            r'sodium|potassium|chloride|CO2|calcium|magnesium|'
            r'troponin|BNP|lactate|INR|PT|PTT)\s*(?:of\s+)?[\d.]+',
        ],
    }
    
    # PHI Replacement Templates
    PHI_REPLACEMENTS = {
        PHIType.NAME: "[REDACTED_NAME]",
        PHIType.DATE: "[REDACTED_DATE]",
        PHIType.MRN: "[REDACTED_MRN]",
        PHIType.SSN: "[REDACTED_SSN]",
        PHIType.PHONE: "[REDACTED_PHONE]",
        PHIType.EMAIL: "[REDACTED_EMAIL]",
        PHIType.ADDRESS: "[REDACTED_ADDRESS]",
        PHIType.AGE: "[REDACTED_AGE]",
    }
    
    def __init__(self):
        self._compile_patterns()
    
    def _compile_patterns(self):
        """Pre-compile regex patterns for efficiency."""
        self._phi_compiled = {}
        for phi_type, patterns in self.PHI_PATTERNS.items():
            self._phi_compiled[phi_type] = [
                re.compile(p, re.IGNORECASE) for p in patterns
            ]
        
        self._clinical_compiled = {}
        for entity_type, patterns in self.CLINICAL_PATTERNS.items():
            self._clinical_compiled[entity_type] = [
                re.compile(p, re.IGNORECASE) for p in patterns
            ]
    
    def detect_phi(self, text: str) -> List[PHIMatch]:
        """
        Detect Protected Health Information in text.
        
        Returns list of PHI matches with positions and types.
        """
        matches = []
        
        for phi_type, patterns in self._phi_compiled.items():
            for pattern in patterns:
                for match in pattern.finditer(text):
                    matches.append(PHIMatch(
                        text=match.group(),
                        phi_type=phi_type,
                        start=match.start(),
                        end=match.end(),
                        replacement=self.PHI_REPLACEMENTS[phi_type],
                    ))
        
        # Sort by position and remove overlaps
        matches.sort(key=lambda x: x.start)
        return self._remove_overlapping(matches)
    
    def _remove_overlapping(self, matches: List[PHIMatch]) -> List[PHIMatch]:
        """Remove overlapping PHI matches, keeping longest."""
        if not matches:
            return []
        
        result = [matches[0]]
        for match in matches[1:]:
            if match.start >= result[-1].end:
                result.append(match)
            elif match.end - match.start > result[-1].end - result[-1].start:
                result[-1] = match
        
        return result
    
    def deidentify(self, text: str) -> Tuple[str, List[PHIMatch]]:
        """
        Remove PHI from text.
        
        Returns:
            - Cleaned text with PHI replaced
            - List of PHI matches found
        """
        phi_matches = self.detect_phi(text)
        
        # Replace from end to preserve positions
        deid_text = text
        for match in reversed(phi_matches):
            deid_text = deid_text[:match.start] + match.replacement + deid_text[match.end:]
        
        return deid_text, phi_matches
    
    def extract_entities(self, text: str) -> List[Entity]:
        """
        Extract clinical entities from text.
        
        Returns list of entities (diseases, drugs, procedures, etc.)
        """
        entities = []
        
        for entity_type, patterns in self._clinical_compiled.items():
            for pattern in patterns:
                for match in pattern.finditer(text):
                    entities.append(Entity(
                        text=match.group(),
                        label=entity_type.value,
                        start=match.start(),
                        end=match.end(),
                    ))
        
        # Sort by position
        entities.sort(key=lambda x: x.start)
        return entities
    
    def process_clinical_note(self, text: str) -> Dict[str, Any]:
        """
        Full processing pipeline for a clinical note.
        
        Steps:
        1. De-identify PHI
        2. Extract clinical entities
        3. Prepare for embedding
        """
        # Step 1: De-identify
        deid_text, phi_matches = self.deidentify(text)
        
        # Step 2: Extract entities from de-identified text
        entities = self.extract_entities(deid_text)
        
        # Step 3: Group entities by type
        entities_by_type = {}
        for entity in entities:
            if entity.label not in entities_by_type:
                entities_by_type[entity.label] = []
            entities_by_type[entity.label].append(entity.text)
        
        # Deduplicate
        for label in entities_by_type:
            entities_by_type[label] = list(set(entities_by_type[label]))
        
        # Step 4: Prepare embedding-ready text (cleaned, normalized)
        embedding_text = self._prepare_for_embedding(deid_text)
        
        return {
            "original_length": len(text),
            "deidentified_text": deid_text,
            "phi_removed": [
                {"text": m.text, "type": m.phi_type.value, "replacement": m.replacement}
                for m in phi_matches
            ],
            "phi_count": len(phi_matches),
            "entities": [
                {"text": e.text, "label": e.label, "start": e.start, "end": e.end}
                for e in entities
            ],
            "entities_by_type": entities_by_type,
            "entity_count": len(entities),
            "embedding_ready_text": embedding_text,
            "processed_at": datetime.utcnow().isoformat(),
        }
    
    def _prepare_for_embedding(self, text: str) -> str:
        """
        Prepare text for embedding/RAG.
        
        Normalizes whitespace, removes excessive punctuation.
        """
        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove repeated punctuation
        text = re.sub(r'([.!?])\1+', r'\1', text)
        # Strip
        text = text.strip()
        return text
    
    def summarize_entities(self, text: str) -> str:
        """
        Create a structured summary of clinical entities.
        
        Returns a formatted summary string.
        """
        entities = self.extract_entities(text)
        
        # Group by type
        by_type = {}
        for entity in entities:
            if entity.label not in by_type:
                by_type[entity.label] = set()
            by_type[entity.label].add(entity.text.lower())
        
        # Format summary
        lines = ["Clinical Summary:"]
        
        if EntityType.DISEASE.value in by_type:
            lines.append(f"  Conditions: {', '.join(by_type[EntityType.DISEASE.value])}")
        if EntityType.DRUG.value in by_type:
            lines.append(f"  Medications: {', '.join(by_type[EntityType.DRUG.value])}")
        if EntityType.PROCEDURE.value in by_type:
            lines.append(f"  Procedures: {', '.join(by_type[EntityType.PROCEDURE.value])}")
        if EntityType.VITAL_SIGN.value in by_type:
            lines.append(f"  Vitals: {', '.join(by_type[EntityType.VITAL_SIGN.value])}")
        if EntityType.LAB_VALUE.value in by_type:
            lines.append(f"  Labs: {', '.join(by_type[EntityType.LAB_VALUE.value])}")
        
        return '\n'.join(lines)


# Global singleton
_nlp_pipeline: Optional[ClinicalNLPPipeline] = None


def get_nlp_pipeline() -> ClinicalNLPPipeline:
    """Get or create NLP pipeline instance."""
    global _nlp_pipeline
    if _nlp_pipeline is None:
        _nlp_pipeline = ClinicalNLPPipeline()
    return _nlp_pipeline
