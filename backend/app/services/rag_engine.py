"""
RAG Pipeline - Knowledge Base Retrieval

Implements Retrieval-Augmented Generation for clinical knowledge:
- Document chunking (recursive character splitter)
- Embedding generation (all-MiniLM-L6-v2)
- Vector store (in-memory, Supabase-ready)
- Hybrid search (dense + keyword)
- Re-ranking and hallucination control
"""
import re
import json
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
import hashlib

from ..core.database import get_supabase_client


@dataclass
class Document:
    """A document in the knowledge base."""
    doc_id: str
    title: str
    content: str
    source: str
    doc_type: str  # sop, guideline, policy, note
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class Chunk:
    """A chunk of a document."""
    chunk_id: str
    doc_id: str
    content: str
    position: int  # Position in document (0-indexed)
    embedding: Optional[List[float]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SearchResult:
    """A search result with relevance score."""
    chunk: Chunk
    score: float
    source_doc: Optional[Document] = None
    match_type: str = "dense"  # dense, keyword, hybrid


class TextChunker:
    """
    Recursive character text splitter.
    
    Splits text into overlapping chunks for better context preservation.
    """
    
    def __init__(
        self, 
        chunk_size: int = 512, 
        chunk_overlap: int = 50,
        separators: List[str] = None
    ):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.separators = separators or ["\n\n", "\n", ". ", " ", ""]
    
    def split_text(self, text: str) -> List[str]:
        """Split text into chunks using recursive splitting."""
        return self._split_recursive(text, self.separators)
    
    def _split_recursive(self, text: str, separators: List[str]) -> List[str]:
        """Recursively split text using available separators."""
        if not separators:
            return [text]
        
        separator = separators[0]
        remaining_separators = separators[1:]
        
        if separator == "":
            # Character-level split
            chunks = []
            for i in range(0, len(text), self.chunk_size - self.chunk_overlap):
                chunk = text[i:i + self.chunk_size]
                if chunk:
                    chunks.append(chunk)
            return chunks
        
        splits = text.split(separator)
        chunks = []
        current_chunk = ""
        
        for split in splits:
            if len(current_chunk) + len(split) + len(separator) <= self.chunk_size:
                current_chunk += (separator if current_chunk else "") + split
            else:
                if current_chunk:
                    chunks.append(current_chunk)
                
                if len(split) > self.chunk_size:
                    # Recursively split large pieces
                    sub_chunks = self._split_recursive(split, remaining_separators)
                    chunks.extend(sub_chunks)
                    current_chunk = ""
                else:
                    current_chunk = split
        
        if current_chunk:
            chunks.append(current_chunk)
        
        # Add overlap
        overlapped_chunks = []
        for i, chunk in enumerate(chunks):
            if i > 0 and len(chunks[i-1]) >= self.chunk_overlap:
                # Prepend overlap from previous chunk
                overlap = chunks[i-1][-self.chunk_overlap:]
                chunk = overlap + " " + chunk
            overlapped_chunks.append(chunk.strip())
        
        return overlapped_chunks


class EmbeddingModel:
    """
    Embedding model wrapper.
    
    Uses sentence-transformers all-MiniLM-L6-v2 for generating embeddings.
    Falls back to simple TF-IDF-like embeddings if model not available.
    """
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model_name = model_name
        self.model = None
        self.dimension = 384  # MiniLM dimension
        self._load_model()
    
    def _load_model(self):
        """Load the embedding model."""
        try:
            from sentence_transformers import SentenceTransformer
            print(f"📦 Loading embedding model: {self.model_name}...")
            self.model = SentenceTransformer(self.model_name)
            print(f"   ✓ Model loaded successfully")
        except Exception as e:
            print(f"   ⚠ Could not load model: {e}")
            print(f"   Using fallback hash-based embeddings")
            self.model = None
    
    def embed(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for texts."""
        if self.model is not None:
            embeddings = self.model.encode(texts, convert_to_numpy=True)
            return embeddings.tolist()
        else:
            # Fallback: simple hash-based pseudo-embeddings
            return [self._fallback_embed(t) for t in texts]
    
    def embed_single(self, text: str) -> List[float]:
        """Generate embedding for a single text."""
        return self.embed([text])[0]
    
    def _fallback_embed(self, text: str) -> List[float]:
        """Simple fallback embedding using hash."""
        # Create reproducible pseudo-embedding from text hash
        text_hash = hashlib.md5(text.encode()).hexdigest()
        np.random.seed(int(text_hash[:8], 16))
        return np.random.randn(self.dimension).tolist()


class VectorStore:
    """
    In-memory vector store with similarity search.
    
    Also persists to Supabase for production use.
    """
    
    def __init__(self, embedding_model: EmbeddingModel):
        self.embedding_model = embedding_model
        self.chunks: Dict[str, Chunk] = {}
        self.documents: Dict[str, Document] = {}
        self.supabase = get_supabase_client()
    
    def add_document(self, document: Document) -> List[str]:
        """Add a document to the store, return chunk IDs."""
        self.documents[document.doc_id] = document
        
        # Save document to Supabase
        if self.supabase:
            try:
                doc_data = {
                    "doc_id": document.doc_id,
                    "title": document.title,
                    "content": document.content,
                    "metadata": {
                        "source": document.source,
                        "doc_type": document.doc_type,
                    },
                    "created_at": document.created_at.isoformat() if hasattr(document.created_at, 'isoformat') else str(document.created_at)
                }
                self.supabase.table("documents").upsert(doc_data, on_conflict="doc_id").execute()
            except Exception as e:
                print(f"[RAG] Failed to save document to DB: {e}")
        
        # Chunk the document
        chunker = TextChunker(chunk_size=512, chunk_overlap=50)
        text_chunks = chunker.split_text(document.content)
        
        chunk_ids = []
        for i, text in enumerate(text_chunks):
            chunk_id = f"{document.doc_id}_chunk_{i}"
            
            # Generate embedding
            embedding = self.embedding_model.embed_single(text)
            
            chunk = Chunk(
                chunk_id=chunk_id,
                doc_id=document.doc_id,
                content=text,
                position=i,
                embedding=embedding,
                metadata={
                    "title": document.title,
                    "source": document.source,
                    "doc_type": document.doc_type,
                }
            )
            
            self.chunks[chunk_id] = chunk
            chunk_ids.append(chunk_id)
            
            # Save embedding to Supabase
            if self.supabase:
                try:
                    embed_data = {
                        "doc_id": document.doc_id,
                        "chunk_index": i,
                        "chunk_text": text[:2000],  # Limit text length
                        "embedding": embedding,  # pgvector can handle this
                        "metadata": chunk.metadata,
                        "created_at": datetime.utcnow().isoformat()
                    }
                    self.supabase.table("doc_embeddings").insert(embed_data).execute()
                except Exception as e:
                    print(f"[RAG] Failed to save embedding to DB: {e}")
        
        return chunk_ids
    
    def similarity_search(
        self, 
        query: str, 
        top_k: int = 5,
        threshold: float = 0.3
    ) -> List[SearchResult]:
        """
        Perform dense vector similarity search.
        
        Uses cosine similarity between query and chunk embeddings.
        """
        if not self.chunks:
            return []
        
        # Embed query
        query_embedding = np.array(self.embedding_model.embed_single(query))
        
        # Calculate similarities
        results = []
        for chunk in self.chunks.values():
            if chunk.embedding is None:
                continue
            
            chunk_embedding = np.array(chunk.embedding)
            
            # Cosine similarity
            similarity = np.dot(query_embedding, chunk_embedding) / (
                np.linalg.norm(query_embedding) * np.linalg.norm(chunk_embedding) + 1e-8
            )
            
            if similarity >= threshold:
                results.append(SearchResult(
                    chunk=chunk,
                    score=float(similarity),
                    source_doc=self.documents.get(chunk.doc_id),
                    match_type="dense",
                ))
        
        # Sort by score
        results.sort(key=lambda x: x.score, reverse=True)
        return results[:top_k]
    
    def keyword_search(self, query: str, top_k: int = 5) -> List[SearchResult]:
        """
        Simple keyword (BM25-like) search.
        
        Finds chunks containing query terms.
        """
        query_terms = set(query.lower().split())
        
        results = []
        for chunk in self.chunks.values():
            chunk_terms = set(chunk.content.lower().split())
            
            # Calculate term overlap score
            overlap = len(query_terms & chunk_terms)
            if overlap > 0:
                score = overlap / len(query_terms)
                results.append(SearchResult(
                    chunk=chunk,
                    score=score,
                    source_doc=self.documents.get(chunk.doc_id),
                    match_type="keyword",
                ))
        
        results.sort(key=lambda x: x.score, reverse=True)
        return results[:top_k]
    
    def hybrid_search(
        self, 
        query: str, 
        top_k: int = 5,
        alpha: float = 0.7,  # Weight for dense vs keyword
        threshold: float = 0.3
    ) -> List[SearchResult]:
        """
        Hybrid search combining dense and keyword retrieval.
        
        Args:
            alpha: Weight for dense search (1-alpha for keyword)
            threshold: Minimum score to include result
        """
        # Get results from both methods
        dense_results = self.similarity_search(query, top_k=top_k * 2, threshold=0.1)
        keyword_results = self.keyword_search(query, top_k=top_k * 2)
        
        # Combine scores
        combined = {}
        
        for result in dense_results:
            combined[result.chunk.chunk_id] = {
                "chunk": result.chunk,
                "dense_score": result.score,
                "keyword_score": 0.0,
                "source_doc": result.source_doc,
            }
        
        for result in keyword_results:
            if result.chunk.chunk_id in combined:
                combined[result.chunk.chunk_id]["keyword_score"] = result.score
            else:
                combined[result.chunk.chunk_id] = {
                    "chunk": result.chunk,
                    "dense_score": 0.0,
                    "keyword_score": result.score,
                    "source_doc": result.source_doc,
                }
        
        # Calculate hybrid scores and create results
        hybrid_results = []
        for chunk_id, data in combined.items():
            hybrid_score = alpha * data["dense_score"] + (1 - alpha) * data["keyword_score"]
            
            if hybrid_score >= threshold:
                hybrid_results.append(SearchResult(
                    chunk=data["chunk"],
                    score=hybrid_score,
                    source_doc=data["source_doc"],
                    match_type="hybrid",
                ))
        
        # Sort and return top-k
        hybrid_results.sort(key=lambda x: x.score, reverse=True)
        return hybrid_results[:top_k]


class RAGEngine:
    """
    Complete RAG pipeline for clinical knowledge retrieval.
    
    Features:
    - Document ingestion and chunking
    - Vector embeddings (all-MiniLM-L6-v2)
    - Hybrid search (dense + keyword)
    - Re-ranking
    - Hallucination control
    """
    
    # Similarity threshold for "sufficient context"
    CONFIDENCE_THRESHOLD = 0.4
    
    def __init__(self):
        self.embedding_model = EmbeddingModel()
        self.vector_store = VectorStore(self.embedding_model)
        self._load_sample_documents()
    
    def _load_sample_documents(self):
        """Load sample clinical documents for demo."""
        sample_docs = [
            Document(
                doc_id="sop-001",
                title="ICU Capacity Management SOP",
                content="""
                Standard Operating Procedure: ICU Capacity Management
                
                Purpose: This SOP outlines procedures for managing ICU bed capacity during high-occupancy periods.
                
                Thresholds:
                - Warning: ICU occupancy reaches 80%
                - Critical: ICU occupancy reaches 90%
                
                Actions when Warning threshold is reached:
                1. Review all ICU patients for step-down eligibility
                2. Contact charge nurse to assess discharge-ready patients
                3. Notify attending physicians of capacity concerns
                4. Prepare step-down unit beds for potential transfers
                
                Actions when Critical threshold is reached:
                1. Activate ICU surge protocol
                2. Contact hospital administrator on-call
                3. Consider transfer to affiliated facilities
                4. Implement elective surgery postponement if needed
                5. Document all capacity decisions in the system
                
                Patient Selection for Transfer:
                - Patients with stable vital signs for >24 hours
                - No active vasoactive medication drips
                - No high-flow oxygen requirement (>6L)
                - Discharge readiness score >70%
                """,
                source="Hospital Policy Manual v2.3",
                doc_type="sop",
            ),
            Document(
                doc_id="sop-002",
                title="Sepsis Bundle Protocol",
                content="""
                Sepsis Management Bundle - Hour-1 Protocol
                
                Immediate Actions (within 1 hour of sepsis identification):
                
                1. Lactate Measurement
                   - Order serum lactate level
                   - If lactate >2 mmol/L, repeat within 2-4 hours
                
                2. Blood Cultures
                   - Obtain 2 sets of blood cultures before antibiotics
                   - Include aerobic and anaerobic bottles
                
                3. Broad-Spectrum Antibiotics
                   - Administer within 1 hour of recognition
                   - Coverage: gram-positive, gram-negative, and anaerobes
                   - Recommended: Piperacillin-tazobactam + Vancomycin
                
                4. Fluid Resuscitation
                   - 30 mL/kg crystalloid for hypotension or lactate ≥4
                   - Reassess volume status and tissue perfusion
                
                5. Vasopressors
                   - If hypotension persists after fluid resuscitation
                   - Target MAP ≥65 mmHg
                   - First-line: Norepinephrine
                
                Documentation Requirements:
                - Time of sepsis identification
                - Time of each bundle element completion
                - Patient response to interventions
                """,
                source="Infectious Disease Guidelines 2024",
                doc_type="guideline",
            ),
            Document(
                doc_id="sop-003",
                title="Discharge Planning Guidelines",
                content="""
                Discharge Planning and Readmission Prevention
                
                Discharge Readiness Criteria:
                1. Stable vital signs for minimum 24 hours
                2. Oral medication tolerance established
                3. Adequate pain control with oral medications
                4. Patient/family education completed
                5. Follow-up appointments scheduled
                6. Home care services arranged if needed
                
                High-Risk Patient Identification:
                - Age >65 with multiple comorbidities
                - Previous admission within 30 days
                - Social determinants of health concerns
                - Complex medication regimen (>5 medications)
                - Inadequate social support
                
                Readmission Prevention Strategies:
                1. Medication reconciliation before discharge
                2. Teach-back method for patient education
                3. Schedule follow-up within 7 days for high-risk patients
                4. Post-discharge phone call within 48 hours
                5. Connect with community health resources
                
                Documentation:
                - Discharge summary within 24 hours
                - Medication list provided to patient
                - Warning signs for return to ED
                """,
                source="Care Transitions Protocol",
                doc_type="guideline",
            ),
        ]
        
        print("📚 Loading sample documents into RAG...")
        for doc in sample_docs:
            chunk_ids = self.vector_store.add_document(doc)
            print(f"   ✓ {doc.title}: {len(chunk_ids)} chunks")
    
    def add_document(self, document: Document) -> Dict[str, Any]:
        """Add a document to the knowledge base."""
        chunk_ids = self.vector_store.add_document(document)
        return {
            "doc_id": document.doc_id,
            "title": document.title,
            "chunks_created": len(chunk_ids),
            "chunk_ids": chunk_ids,
        }
    
    def search(
        self, 
        query: str, 
        top_k: int = 3,
        search_type: str = "hybrid"
    ) -> Dict[str, Any]:
        """
        Search the knowledge base.
        
        Args:
            query: Search query
            top_k: Number of results to return
            search_type: 'dense', 'keyword', or 'hybrid'
        """
        if search_type == "dense":
            results = self.vector_store.similarity_search(query, top_k=top_k)
        elif search_type == "keyword":
            results = self.vector_store.keyword_search(query, top_k=top_k)
        else:
            results = self.vector_store.hybrid_search(query, top_k=top_k)
        
        # Check for sufficient context
        has_sufficient_context = any(r.score >= self.CONFIDENCE_THRESHOLD for r in results)
        
        return {
            "query": query,
            "search_type": search_type,
            "results": [
                {
                    "chunk_id": r.chunk.chunk_id,
                    "content": r.chunk.content[:500] + "..." if len(r.chunk.content) > 500 else r.chunk.content,
                    "score": round(r.score, 4),
                    "source": {
                        "doc_id": r.chunk.doc_id,
                        "title": r.chunk.metadata.get("title", "Unknown"),
                        "doc_type": r.chunk.metadata.get("doc_type", "unknown"),
                    },
                    "match_type": r.match_type,
                }
                for r in results
            ],
            "result_count": len(results),
            "has_sufficient_context": has_sufficient_context,
            "confidence_note": None if has_sufficient_context else "Insufficient context found. Results may not fully answer the query.",
        }
    
    def get_context_for_agent(self, query: str, top_k: int = 3) -> Dict[str, Any]:
        """
        Retrieve context for agent planning.
        
        Returns formatted context with citations for the Planning Agent.
        """
        search_result = self.search(query, top_k=top_k, search_type="hybrid")
        
        # Format context with citations
        context_parts = []
        sources = []
        
        for i, result in enumerate(search_result["results"], 1):
            citation = f"[{i}]"
            context_parts.append(f"{citation} {result['content']}")
            sources.append({
                "citation": citation,
                "doc_id": result["source"]["doc_id"],
                "title": result["source"]["title"],
                "score": result["score"],
            })
        
        combined_context = "\n\n".join(context_parts)
        
        return {
            "query": query,
            "context": combined_context,
            "sources": sources,
            "has_sufficient_context": search_result["has_sufficient_context"],
            "warning": search_result.get("confidence_note"),
        }
    
    def get_stats(self) -> Dict[str, Any]:
        """Get knowledge base statistics."""
        return {
            "total_documents": len(self.vector_store.documents),
            "total_chunks": len(self.vector_store.chunks),
            "embedding_model": self.embedding_model.model_name,
            "embedding_dimension": self.embedding_model.dimension,
            "confidence_threshold": self.CONFIDENCE_THRESHOLD,
        }


# Global singleton
_rag_engine: Optional[RAGEngine] = None


def get_rag_engine() -> RAGEngine:
    """Get or create RAG engine instance."""
    global _rag_engine
    if _rag_engine is None:
        _rag_engine = RAGEngine()
    return _rag_engine
