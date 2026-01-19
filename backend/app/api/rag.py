"""
API Routes - RAG endpoint.
Provides knowledge base search and retrieval.
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List, Optional

from ..services.rag_engine import get_rag_engine, Document

router = APIRouter(prefix="/rag", tags=["RAG Knowledge Base"])


class SearchQuery(BaseModel):
    """Search query input."""
    query: str
    top_k: int = 3
    search_type: str = "hybrid"  # dense, keyword, hybrid


class DocumentInput(BaseModel):
    """Input for adding a document."""
    title: str
    content: str
    source: str
    doc_type: str = "guideline"  # sop, guideline, policy, note


@router.post("/search")
async def search_knowledge_base(query: SearchQuery) -> Dict[str, Any]:
    """
    Search the clinical knowledge base.
    
    Search types:
    - dense: Vector similarity search
    - keyword: Term matching (BM25-like)
    - hybrid: Combined dense + keyword (recommended)
    
    Returns matched chunks with relevance scores and source citations.
    """
    if not query.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")
    
    if query.search_type not in ["dense", "keyword", "hybrid"]:
        raise HTTPException(status_code=400, detail="Invalid search_type. Use: dense, keyword, or hybrid")
    
    engine = get_rag_engine()
    return engine.search(query.query, top_k=query.top_k, search_type=query.search_type)


@router.post("/context")
async def get_context_for_agent(query: SearchQuery) -> Dict[str, Any]:
    """
    Get formatted context for agent planning.
    
    Returns context with citations formatted for the Planning Agent.
    Includes hallucination check (has_sufficient_context flag).
    """
    if not query.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")
    
    engine = get_rag_engine()
    return engine.get_context_for_agent(query.query, top_k=query.top_k)


@router.post("/documents")
async def add_document(doc: DocumentInput) -> Dict[str, Any]:
    """
    Add a document to the knowledge base.
    
    Document is automatically chunked and embedded.
    """
    if not doc.content.strip():
        raise HTTPException(status_code=400, detail="Document content cannot be empty")
    
    engine = get_rag_engine()
    
    # Generate doc ID from title
    doc_id = f"doc-{len(engine.vector_store.documents) + 1:03d}"
    
    document = Document(
        doc_id=doc_id,
        title=doc.title,
        content=doc.content,
        source=doc.source,
        doc_type=doc.doc_type,
    )
    
    result = engine.add_document(document)
    return result


@router.get("/documents")
async def list_documents() -> Dict[str, Any]:
    """
    List all documents in the knowledge base.
    """
    engine = get_rag_engine()
    
    documents = []
    for doc in engine.vector_store.documents.values():
        documents.append({
            "doc_id": doc.doc_id,
            "title": doc.title,
            "source": doc.source,
            "doc_type": doc.doc_type,
            "content_preview": doc.content[:200] + "..." if len(doc.content) > 200 else doc.content,
            "created_at": doc.created_at.isoformat(),
        })
    
    return {
        "count": len(documents),
        "documents": documents,
    }


@router.get("/documents/{doc_id}")
async def get_document(doc_id: str) -> Dict[str, Any]:
    """
    Get a specific document by ID.
    """
    engine = get_rag_engine()
    
    if doc_id not in engine.vector_store.documents:
        raise HTTPException(status_code=404, detail=f"Document {doc_id} not found")
    
    doc = engine.vector_store.documents[doc_id]
    
    # Get chunk count
    chunk_count = sum(1 for c in engine.vector_store.chunks.values() if c.doc_id == doc_id)
    
    return {
        "doc_id": doc.doc_id,
        "title": doc.title,
        "content": doc.content,
        "source": doc.source,
        "doc_type": doc.doc_type,
        "chunk_count": chunk_count,
        "created_at": doc.created_at.isoformat(),
    }


@router.get("/stats")
async def get_knowledge_base_stats() -> Dict[str, Any]:
    """
    Get knowledge base statistics.
    """
    engine = get_rag_engine()
    return engine.get_stats()


@router.get("/status")
async def rag_status() -> Dict[str, Any]:
    """Get RAG engine status."""
    engine = get_rag_engine()
    stats = engine.get_stats()
    
    return {
        "status": "operational",
        "engine": "Hybrid RAG (Dense + Keyword)",
        "embedding_model": stats["embedding_model"],
        "features": {
            "document_chunking": True,
            "vector_embeddings": True,
            "dense_search": True,
            "keyword_search": True,
            "hybrid_search": True,
            "hallucination_control": True,
        },
        "knowledge_base": {
            "documents": stats["total_documents"],
            "chunks": stats["total_chunks"],
        }
    }
