from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List


# ============================================
# Chat Models
# ============================================
class ChatMessageBase(BaseModel):
    """Base chat message schema."""
    content: str
    sender: str  # "user" or "assistant"
    message_type: str = "text"  # "text", "voice", etc.


class ChatMessageCreate(ChatMessageBase):
    """Create chat message schema."""
    pass


class ChatMessage(ChatMessageBase):
    """Chat message schema with metadata."""
    id: int
    session_id: str
    created_at: datetime
    metadata: Optional[dict] = None
    
    class Config:
        from_attributes = True


class ChatSessionCreate(BaseModel):
    """Create chat session schema."""
    title: Optional[str] = "New Chat"


class ChatSession(BaseModel):
    """Chat session schema."""
    id: str
    title: str
    created_at: datetime
    updated_at: datetime
    messages: List[ChatMessage] = []
    
    class Config:
        from_attributes = True


# ============================================
# RAG & Query Models
# ============================================
class RagQuery(BaseModel):
    """RAG search query."""
    query: str
    top_k: int = Field(default=5, ge=1, le=50)
    threshold: float = Field(default=0.5, ge=0.0, le=1.0)


class RagResult(BaseModel):
    """RAG search result."""
    content: str
    score: float
    metadata: Optional[dict] = None


class RagResponse(BaseModel):
    """RAG search response."""
    results: List[RagResult]
    query: str
    count: int


# ============================================
# LLM Response Models
# ============================================
class LlmQueryRouter(BaseModel):
    """Query routing decision."""
    query_type: str  # "chat", "rag", "tool"
    confidence: float
    tool_name: Optional[str] = None
    rag_required: bool = False


class LlmResponse(BaseModel):
    """LLM generation response."""
    response: str
    sources: List[str] = []
    query_routing: LlmQueryRouter
    tokens_used: Optional[dict] = None


# ============================================
# Chat Endpoint Models
# ============================================
class ChatRequest(BaseModel):
    """Chat request."""
    message: str
    session_id: str
    use_rag: Optional[bool] = True
    use_tools: Optional[bool] = True


class ChatResponse(BaseModel):
    """Chat response."""
    response: str
    session_id: str
    message_id: int
    sources: List[str] = []
    tool_calls: Optional[List[str]] = None


# ============================================
# Speech Models
# ============================================
class SpeechToTextRequest(BaseModel):
    """Speech to text conversion request."""
    audio_file: Optional[str] = None  # Base64 encoded audio


class SpeechToTextResponse(BaseModel):
    """Speech to text response."""
    text: str
    confidence: Optional[float] = None
    language: str = "en"


class TextToSpeechRequest(BaseModel):
    """Text to speech request."""
    text: str
    voice: str = "default"


# ============================================
# Error Models
# ============================================
class ErrorResponse(BaseModel):
    """Error response."""
    detail: str
    code: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
