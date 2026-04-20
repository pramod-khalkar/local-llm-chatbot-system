from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.models.database import Base


class User(Base):
    """User model."""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(255), unique=True, index=True)
    email = Column(String(255), unique=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    sessions = relationship("ChatSessionORM", back_populates="user")


class ChatSessionORM(Base):
    """Chat session model."""
    __tablename__ = "chat_sessions"
    
    id = Column(String(36), primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    title = Column(String(255), default="New Chat")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    session_metadata = Column(JSON, default={})
    
    # Relationships
    user = relationship("User", back_populates="sessions")
    messages = relationship("ChatMessageORM", back_populates="session", cascade="all, delete-orphan")


class ChatMessageORM(Base):
    """Chat message model."""
    __tablename__ = "chat_messages"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(36), ForeignKey("chat_sessions.id"), index=True)
    content = Column(Text)
    sender = Column(String(50))  # "user" or "assistant"
    message_type = Column(String(50), default="text")  # "text", "voice", etc.
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    message_metadata = Column(JSON, default={})
    
    # Relationships
    session = relationship("ChatSessionORM", back_populates="messages")


class DocumentChunk(Base):
    """Document chunk for RAG."""
    __tablename__ = "document_chunks"
    
    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(String(255), index=True)
    content = Column(Text)
    chunk_index = Column(Integer)
    embedding = Column(JSON)  # Store embedding metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    chunk_metadata = Column(JSON, default={})


class QueryLog(Base):
    """Query logging for analytics and debugging."""
    __tablename__ = "query_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(36), ForeignKey("chat_sessions.id"))
    query = Column(Text)
    query_type = Column(String(50))  # "chat", "rag", "tool"
    response = Column(Text)
    confidence = Column(String(10))
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    log_metadata = Column(JSON, default={})
