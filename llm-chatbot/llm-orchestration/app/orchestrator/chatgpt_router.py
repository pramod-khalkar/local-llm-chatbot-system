"""
ChatGPT-based routing and parameter extraction for orchestration.
"""
import os
import json
import logging
from typing import Dict, Any, List, Optional
import openai

logger = logging.getLogger(__name__)


class ChatGPTRouter:
    """Routes queries and extracts parameters using ChatGPT."""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-3.5-turbo"):
        """
        Initialize ChatGPT router.
        
        Args:
            api_key: OpenAI API key (defaults to OPENAI_API_KEY env var)
            model: Model to use (default: gpt-3.5-turbo)
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")
        
        self.client = openai.AsyncOpenAI(api_key=self.api_key)
        self.model = model
        logger.info(f"ChatGPT router initialized with model: {model}")
    
    async def route_query(self, query: str, context: Optional[str] = None) -> Dict[str, Any]:
        """
        Route query to determine its type and required tools.
        
        Args:
            query: User query
            context: Optional context
            
        Returns:
            Routing decision with query_type, tool_name, tool_action, rag_required
        """
        try:
            prompt = f"""Analyze this query and decide the routing.

Query: "{query}"
Context: {context if context else "None"}

Determine:
1. query_type: One of ["chat", "tool", "rag"]
   - "chat": General conversation, no tools needed
   - "tool": User wants to call a tool (todo, calendar, search)
   - "rag": User asking about documents/knowledge base

2. tool_name: If tool is needed, which tool? ("todo", "calendar", "search", or "none")

3. tool_action: If tool is todo, what action? ("create", "complete", "list", "update", "delete", or "none")

4. rag_required: Boolean - should we search documents?

Return ONLY valid JSON:
{{
    "query_type": "chat|tool|rag",
    "tool_name": "todo|calendar|search|none",
    "tool_action": "create|complete|list|update|delete|none",
    "rag_required": true|false,
    "confidence": 0.0-1.0
}}

Examples:
- "Create a todo to fix the bug" → {{"query_type": "tool", "tool_name": "todo", "tool_action": "create", "rag_required": false, "confidence": 0.95}}
- "Show my todos" → {{"query_type": "tool", "tool_name": "todo", "tool_action": "list", "rag_required": false, "confidence": 0.95}}
- "Mark todo 5 as done" → {{"query_type": "tool", "tool_name": "todo", "tool_action": "complete", "rag_required": false, "confidence": 0.95}}
- "Tell me about company policies" → {{"query_type": "rag", "tool_name": "none", "tool_action": "none", "rag_required": true, "confidence": 0.90}}
- "Hello, how are you?" → {{"query_type": "chat", "tool_name": "none", "tool_action": "none", "rag_required": false, "confidence": 0.99}}"""
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,  # Lower temperature for consistency
                max_tokens=200
            )
            
            response_text = response.choices[0].message.content.strip()
            logger.info(f"ChatGPT routing response: {response_text}")
            
            # Parse JSON response
            routing = json.loads(response_text)
            
            return {
                "query_type": routing.get("query_type", "chat"),
                "tool_name": routing.get("tool_name", "none"),
                "tool_action": routing.get("tool_action", "none"),
                "rag_required": routing.get("rag_required", False),
                "confidence": routing.get("confidence", 0.5)
            }
        
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse ChatGPT routing response: {e}")
            # Default to chat
            return {
                "query_type": "chat",
                "tool_name": "none",
                "tool_action": "none",
                "rag_required": False,
                "confidence": 0.0
            }
        
        except Exception as e:
            logger.error(f"Error in ChatGPT routing: {str(e)}", exc_info=True)
            # Default to chat on error
            return {
                "query_type": "chat",
                "tool_name": "none",
                "tool_action": "none",
                "rag_required": False,
                "confidence": 0.0
            }
    
    async def extract_todo_params(self, query: str) -> Dict[str, str]:
        """
        Extract todo parameters (title, description) from query.
        
        Args:
            query: User query
            
        Returns:
            Dict with "title" and "description"
        """
        try:
            prompt = f"""Extract todo task details from this request:
"{query}"

Return ONLY a JSON object with exactly:
{{"title": "task title here", "description": "optional description here"}}

Rules:
- title is required, must not be empty
- description is optional, can be empty string
- Keep title concise (under 100 chars)
- Keep description concise (under 200 chars)

Example: {{"title": "Buy groceries", "description": "milk, eggs, bread"}}"""
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,
                max_tokens=150
            )
            
            response_text = response.choices[0].message.content.strip()
            logger.info(f"ChatGPT extraction response: {response_text}")
            
            extracted = json.loads(response_text)
            
            return {
                "title": extracted.get("title", query[:50]),
                "description": extracted.get("description", "")
            }
        
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse todo extraction: {e}")
            return {
                "title": query[:50],
                "description": ""
            }
        
        except Exception as e:
            logger.error(f"Error extracting todo params: {str(e)}", exc_info=True)
            return {
                "title": query[:50],
                "description": ""
            }
    
    async def refine_with_rag_results(self, original_query: str, rag_results: List[str]) -> str:
        """
        Refine LLM response using RAG search results.
        
        Args:
            original_query: Original user query
            rag_results: List of RAG search results (document chunks)
            
        Returns:
            Refined response incorporating RAG results
        """
        try:
            # Format RAG results
            rag_context = "\n\n".join([f"- {result}" for result in rag_results if result])
            
            prompt = f"""You are a helpful assistant. A user asked:

"{original_query}"

Here are relevant documents/information from the knowledge base:

{rag_context}

Using ONLY the information from these documents, provide a helpful and accurate answer to the user's question.
If the documents don't contain relevant information, say so politely."""
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=500
            )
            
            refined_response = response.choices[0].message.content.strip()
            logger.info(f"RAG refinement completed, response length: {len(refined_response)}")
            
            return refined_response
        
        except Exception as e:
            logger.error(f"Error refining with RAG results: {str(e)}", exc_info=True)
            # Return a default message if refinement fails
            return f"I found some relevant information but encountered an error. Original query: {original_query}"
    
    async def extract_todo_id_for_completion(self, query: str) -> Dict[str, Optional[str]]:
        """
        Extract todo ID or title for completion request.
        
        Args:
            query: Completion request query
            
        Returns:
            Dict with "todo_id" and "todo_title"
        """
        try:
            prompt = f"""Extract the todo ID or title from this completion request:
"{query}"

Return ONLY a JSON object with:
{{"todo_id": "id if mentioned (as string)", "todo_title": "title if mentioned"}}

Rules:
- If ID is mentioned, extract it (e.g., "5", "123")
- If title is mentioned, extract it
- If neither mentioned, return empty strings
- Return as string values

Example: {{"todo_id": "5", "todo_title": ""}}
Example: {{"todo_id": "", "todo_title": "Fix bug"}}"""
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,
                max_tokens=100
            )
            
            response_text = response.choices[0].message.content.strip()
            logger.info(f"Todo ID extraction response: {response_text}")
            
            extracted = json.loads(response_text)
            
            return {
                "todo_id": extracted.get("todo_id") or None,
                "todo_title": extracted.get("todo_title") or None
            }
        
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse todo ID extraction: {e}")
            return {"todo_id": None, "todo_title": None}
        
        except Exception as e:
            logger.error(f"Error extracting todo ID: {str(e)}", exc_info=True)
            return {"todo_id": None, "todo_title": None}
