from pydantic import BaseModel
from typing import Optional, List, Dict, Any


class OrchestrationQuery(BaseModel):
    """Orchestration query."""
    query: str
    use_rag: bool = True
    use_tools: bool = True
    context: Optional[str] = None


class OrchestrationResponse(BaseModel):
    """Orchestration response."""
    response: str
    query_type: str
    sources: List[str] = []
    tool_calls: List[str] = []
    tokens: Optional[Dict[str, Any]] = None


class RagSearchRequest(BaseModel):
    """RAG search request."""
    query: str
    top_k: int = 5
    threshold: float = 0.5


class RagIndexRequest(BaseModel):
    """RAG index request."""
    documents: List[Dict[str, Any]]
