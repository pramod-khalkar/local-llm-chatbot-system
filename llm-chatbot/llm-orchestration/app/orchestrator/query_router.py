import re
import logging
from typing import Dict, Any, Optional
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class QueryDecision(BaseModel):
    """Query routing decision."""
    query_type: str  # "chat", "rag", "tool"
    confidence: float  # 0-1
    tool_name: Optional[str] = None
    tool_action: Optional[str] = None  # e.g., "create", "list", "complete" for todos
    rag_required: bool = False
    rationale: str


class QueryRouter:
    """Intelligent query router for chat, RAG, and tool calls."""
    
    def __init__(self):
        # Tool keywords
        self.tool_keywords = {
            "todo": ["todo", "task", "create", "list", "complete", "reminder", "schedule"],
            "calendar": ["calendar", "schedule", "event", "meeting", "date", "time"],
            "search": ["search", "find", "look for", "find information", "research"]
        }
        
        # RAG keywords
        self.rag_keywords = [
            "document", "file", "reference", "according to", "based on",
            "search my documents", "look up", "find in my files", "retrieve"
        ]
        
        # Action keywords for todos
        self.todo_actions = {
            "create": ["add", "create", "new", "make", "create a todo", "add a task"],
            "list": ["list", "show", "get", "all todos", "all tasks", "what do i have"],
            "complete": ["complete", "done", "finish", "mark done", "close", "complete task"],
            "update": ["update", "change", "modify", "edit"],
            "delete": ["delete", "remove", "clear"]
        }
    
    async def route_query(self, query: str, context: Optional[str] = None) -> QueryDecision:
        """Route query to appropriate handler."""
        try:
            query_lower = query.lower()
            logger.info(f"Query router: processing query_lower='{query_lower}'")
            
            # Check for tool calls
            tool_decision = self._detect_tool_intent(query_lower)
            logger.info(f"Query router: tool_decision={tool_decision}")
            if tool_decision:
                logger.info(f"Query router: Tool intent detected - {tool_decision.tool_name}")
                return tool_decision
            
            # Check for RAG requirement
            rag_required = self._should_use_rag(query_lower)
            logger.info(f"Query router: rag_required={rag_required}")
            
            # Check for complex query (might benefit from RAG + chat)
            if rag_required:
                return QueryDecision(
                    query_type="hybrid",
                    confidence=0.8,
                    rag_required=True,
                    rationale="Query mentions documents or requires knowledge base search"
                )
            
            # Default to chat
            logger.info("Query router: Defaulting to chat")
            return QueryDecision(
                query_type="chat",
                confidence=0.9,
                rag_required=False,
                rationale="General conversation query"
            )
        
        except Exception as e:
            logger.error(f"Error routing query: {str(e)}")
            # Default to safe chat mode
            return QueryDecision(
                query_type="chat",
                confidence=0.5,
                rag_required=False,
                rationale="Error during routing, defaulting to chat"
            )
    
    def _detect_tool_intent(self, query: str) -> Optional[QueryDecision]:
        """Detect if query requires tool call."""
        for tool, keywords in self.tool_keywords.items():
            for keyword in keywords:
                if keyword in query:
                    confidence = len([k for k in keywords if k in query]) / len(keywords)
                    
                    # Detect action for todos
                    tool_action = None
                    if tool == "todo":
                        tool_action = self._detect_todo_action(query)
                    
                    return QueryDecision(
                        query_type="tool",
                        confidence=min(0.9, 0.6 + confidence * 0.3),
                        tool_name=tool,
                        tool_action=tool_action,
                        rag_required=False,
                        rationale=f"Query contains tool keywords for {tool}" + (f", action: {tool_action}" if tool_action else "")
                    )
        
        return None
    
    def _detect_todo_action(self, query: str) -> Optional[str]:
        """Detect the action for a todo query (create, list, complete, etc.)."""
        for action, keywords in self.todo_actions.items():
            for keyword in keywords:
                if keyword in query:
                    return action
        return "list"  # Default to list if no specific action detected
    
    def _should_use_rag(self, query: str) -> bool:
        """Check if query requires RAG."""
        for keyword in self.rag_keywords:
            if keyword in query:
                return True
        
        # Check for question patterns that might benefit from context
        if any(pattern in query for pattern in ["what is", "explain", "define", "how to"]):
            return False  # General knowledge questions don't need RAG
        
        return False
    
    def get_routing_stats(self) -> Dict[str, Any]:
        """Get routing statistics and configuration."""
        return {
            "tools": list(self.tool_keywords.keys()),
            "rag_keywords": self.rag_keywords,
            "routing_types": ["chat", "rag", "tool", "hybrid"]
        }
