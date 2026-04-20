from fastapi import APIRouter, Depends, HTTPException, File, UploadFile
from sqlalchemy.orm import Session
from typing import List
from app.models.database import get_db
from app.models.schemas import ChatRequest, ChatResponse, ChatSession, ChatMessage, ErrorResponse
from app.models.orm_models import ChatSessionORM, ChatMessageORM
from app.utils.logger import logger
import uuid
import httpx

router = APIRouter(prefix="/api/chat", tags=["Chat"])


@router.post("/sessions", response_model=ChatSession)
async def create_chat_session(
    title: str = "New Chat",
    db: Session = Depends(get_db)
) -> ChatSession:
    """Create a new chat session."""
    try:
        session_id = str(uuid.uuid4())
        session = ChatSessionORM(
            id=session_id,
            title=title,
        )
        db.add(session)
        db.commit()
        db.refresh(session)
        return ChatSession(**{
            "id": session.id,
            "title": session.title,
            "created_at": session.created_at,
            "updated_at": session.updated_at,
            "messages": []
        })
    except Exception as e:
        logger.error(f"Error creating session: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create session")


@router.get("/sessions/{session_id}", response_model=ChatSession)
async def get_chat_session(
    session_id: str,
    db: Session = Depends(get_db)
) -> ChatSession:
    """Get chat session with all messages."""
    try:
        session = db.query(ChatSessionORM).filter(ChatSessionORM.id == session_id).first()
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        messages = [
            ChatMessage(**{
                "id": msg.id,
                "content": msg.content,
                "sender": msg.sender,
                "message_type": msg.message_type,
                "session_id": msg.session_id,
                "created_at": msg.created_at,
                "metadata": msg.message_metadata
            })
            for msg in session.messages
        ]
        
        return ChatSession(**{
            "id": session.id,
            "title": session.title,
            "created_at": session.created_at,
            "updated_at": session.updated_at,
            "messages": messages
        })
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting session: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get session")


@router.post("/message", response_model=ChatResponse)
async def send_message(
    request: ChatRequest,
    db: Session = Depends(get_db)
) -> ChatResponse:
    """Send a message in a session."""
    try:
        session = db.query(ChatSessionORM).filter(ChatSessionORM.id == request.session_id).first()
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Store user message
        user_message = ChatMessageORM(
            session_id=request.session_id,
            content=request.message,
            sender="user",
            message_type="text"
        )
        db.add(user_message)
        db.commit()
        db.refresh(user_message)
        
        logger.info(f"User message stored: {user_message.id}")
        
        # Call LLM orchestration service to get response
        orchestration_url = "http://llm-orchestration:8001/api/orchestrator/chat"
        llm_request = {
            "query": request.message,
            "use_rag": request.use_rag,
            "use_tools": request.use_tools,
            "context": None
        }
        
        logger.info(f"Calling orchestration service at {orchestration_url}")
        
        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                llm_response = await client.post(
                    orchestration_url,
                    json=llm_request
                )
                logger.info(f"Orchestration response status: {llm_response.status_code}")
                llm_response.raise_for_status()
                llm_data = llm_response.json()
                logger.info(f"Orchestration response: {llm_data}")
            
            # Store assistant response message
            assistant_message = ChatMessageORM(
                session_id=request.session_id,
                content=llm_data.get("response", "I couldn't generate a response."),
                sender="assistant",
                message_type="text",
                message_metadata={
                    "sources": llm_data.get("sources", []),
                    "tool_calls": llm_data.get("tool_calls", [])
                }
            )
            db.add(assistant_message)
            db.commit()
            db.refresh(assistant_message)
            
            logger.info(f"Assistant message stored: {assistant_message.id}")
            
            return ChatResponse(**{
                "response": llm_data.get("response", ""),
                "message_id": assistant_message.id,
                "session_id": request.session_id,
                "sources": llm_data.get("sources", []),
                "tool_calls": llm_data.get("tool_calls", [])
            })
        except Exception as e:
            logger.error(f"LLM orchestration error: {type(e).__name__}: {str(e)}")
            # Fallback response if orchestration fails
            error_msg = f"Error from LLM service: {str(e)}"
            logger.info(f"Returning fallback response: {error_msg}")
            return ChatResponse(**{
                "response": error_msg,
                "message_id": user_message.id,
                "session_id": request.session_id,
                "sources": [],
                "tool_calls": []
            })
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error sending message: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to send message")


@router.get("/sessions/{session_id}/messages", response_model=List[ChatMessage])
async def get_session_messages(
    session_id: str,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db)
) -> List[ChatMessage]:
    """Get messages from a session with pagination."""
    try:
        messages = db.query(ChatMessageORM).filter(
            ChatMessageORM.session_id == session_id
        ).offset(skip).limit(limit).all()
        
        return [
            ChatMessage(**{
                "id": msg.id,
                "content": msg.content,
                "sender": msg.sender,
                "message_type": msg.message_type,
                "session_id": msg.session_id,
                "created_at": msg.created_at,
                "metadata": msg.message_metadata
            })
            for msg in messages
        ]
    except Exception as e:
        logger.error(f"Error getting messages: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get messages")
