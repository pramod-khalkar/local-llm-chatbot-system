import os
import json
import logging
import httpx
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional, Dict, Any

# Configure logging
logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
logger = logging.getLogger(__name__)

# External Todo API Configuration
TODO_API_BASE_URL = os.getenv("TODO_API_BASE_URL", "http://localhost:8080")

# Models for request/response handling
class Todo(BaseModel):
    id: Optional[str] = None
    title: str
    description: Optional[str] = None
    status: Optional[str] = "PENDING"
    created_at: Optional[datetime] = None


class TodoCreate(BaseModel):
    title: str
    description: Optional[str] = None


class TodoUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None


# Helper class to interact with external Todo API
class TodoAPIClient:
    def __init__(self, base_url: str = TODO_API_BASE_URL):
        self.base_url = base_url
        self.client = httpx.AsyncClient()
    
    async def create_todo(self, title: str, description: str = "") -> Dict[str, Any]:
        """Create a new todo."""
        try:
            response = await self.client.post(
                f"{self.base_url}/api/todos",
                json={"title": title, "description": description},
                timeout=10.0
            )
            if response.status_code == 201:
                return {"status": "success", "data": response.json()}
            else:
                return {"status": "error", "message": f"Failed to create todo: {response.status_code}"}
        except Exception as e:
            logger.error(f"Error creating todo: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    async def list_todos(self, status: Optional[str] = None, search: Optional[str] = None) -> Dict[str, Any]:
        """List todos with optional filters."""
        try:
            params = {}
            if status:
                params["status"] = status
            if search:
                params["search"] = search
            
            response = await self.client.get(
                f"{self.base_url}/api/todos",
                params=params,
                timeout=10.0
            )
            if response.status_code == 200:
                todos = response.json() if isinstance(response.json(), list) else response.json().get("todos", [])
                return {"status": "success", "todos": todos, "count": len(todos)}
            else:
                return {"status": "error", "message": f"Failed to list todos: {response.status_code}"}
        except Exception as e:
            logger.error(f"Error listing todos: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    async def get_todo(self, todo_id: str) -> Dict[str, Any]:
        """Get a single todo."""
        try:
            response = await self.client.get(
                f"{self.base_url}/api/todos/{todo_id}",
                timeout=10.0
            )
            if response.status_code == 200:
                return {"status": "success", "data": response.json()}
            else:
                return {"status": "error", "message": f"Todo not found: {response.status_code}"}
        except Exception as e:
            logger.error(f"Error getting todo: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    async def update_todo(self, todo_id: str, **kwargs) -> Dict[str, Any]:
        """Update a todo."""
        try:
            response = await self.client.put(
                f"{self.base_url}/api/todos/{todo_id}",
                json=kwargs,
                timeout=10.0
            )
            if response.status_code == 200:
                return {"status": "success", "data": response.json()}
            else:
                return {"status": "error", "message": f"Failed to update todo: {response.status_code}"}
        except Exception as e:
            logger.error(f"Error updating todo: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    async def delete_todo(self, todo_id: str) -> Dict[str, Any]:
        """Delete a todo."""
        try:
            response = await self.client.delete(
                f"{self.base_url}/api/todos/{todo_id}",
                timeout=10.0
            )
            if response.status_code == 204:
                return {"status": "success", "message": "Todo deleted successfully"}
            else:
                return {"status": "error", "message": f"Failed to delete todo: {response.status_code}"}
        except Exception as e:
            logger.error(f"Error deleting todo: {str(e)}")
            return {"status": "error", "message": str(e)}


# Initialize Todo API client
todo_client = TodoAPIClient()

# Create FastAPI app
app = FastAPI(
    title="MCP Todo Manager",
    description="MCP Server for todo task management (proxies to external Todo API)",
    version="1.0.0"
)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "mcp-server"}


@app.get("/tools")
async def get_tools():
    """Get available tools."""
    return {
        "tools": [
            {
                "name": "create_todo",
                "description": "Create a new todo task",
                "params": {"title": "str", "description": "str (optional)"}
            },
            {
                "name": "list_todos",
                "description": "List all todos with optional filters",
                "params": {"status": "str (optional, e.g., PENDING, COMPLETED)", "search": "str (optional)"}
            },
            {
                "name": "get_todo",
                "description": "Get a specific todo by ID",
                "params": {"id": "str"}
            },
            {
                "name": "complete_todo",
                "description": "Mark a todo as complete",
                "params": {"id": "str"}
            },
            {
                "name": "update_todo",
                "description": "Update a todo task",
                "params": {"id": "str", "title": "str (optional)", "description": "str (optional)", "status": "str (optional)"}
            },
            {
                "name": "delete_todo",
                "description": "Delete a todo task",
                "params": {"id": "str"}
            }
        ]
    }


@app.post("/tools/create_todo/call")
async def create_todo_tool(request: Dict[str, Any]):
    """Create a todo via MCP tool."""
    try:
        params = request.get("params", {})
        title = params.get("title")
        description = params.get("description", "")
        
        if not title:
            return {"status": "error", "message": "Title is required"}
        
        result = await todo_client.create_todo(title, description)
        return result
    
    except Exception as e:
        logger.error(f"Error creating todo: {str(e)}")
        return {"status": "error", "message": str(e)}


@app.post("/tools/list_todos/call")
async def list_todos_tool(request: Dict[str, Any]):
    """List all todos via MCP tool."""
    try:
        params = request.get("params", {})
        status = params.get("status")
        search = params.get("search")
        
        result = await todo_client.list_todos(status=status, search=search)
        return result
    
    except Exception as e:
        logger.error(f"Error listing todos: {str(e)}")
        return {"status": "error", "message": str(e)}


@app.post("/tools/get_todo/call")
async def get_todo_tool(request: Dict[str, Any]):
    """Get a specific todo via MCP tool."""
    try:
        params = request.get("params", {})
        todo_id = params.get("id")
        
        if not todo_id:
            return {"status": "error", "message": "ID is required"}
        
        result = await todo_client.get_todo(todo_id)
        return result
    
    except Exception as e:
        logger.error(f"Error getting todo: {str(e)}")
        return {"status": "error", "message": str(e)}


@app.post("/tools/complete_todo/call")
async def complete_todo_tool(request: Dict[str, Any]):
    """Mark a todo as complete via MCP tool."""
    try:
        params = request.get("params", {})
        todo_id = params.get("id")
        
        if not todo_id:
            return {"status": "error", "message": "ID is required"}
        
        result = await todo_client.update_todo(todo_id, status="COMPLETED")
        return result
    
    except Exception as e:
        logger.error(f"Error completing todo: {str(e)}")
        return {"status": "error", "message": str(e)}


@app.post("/tools/update_todo/call")
async def update_todo_tool(request: Dict[str, Any]):
    """Update a todo via MCP tool."""
    try:
        params = request.get("params", {})
        todo_id = params.get("id")
        
        if not todo_id:
            return {"status": "error", "message": "ID is required"}
        
        update_data = {}
        if "title" in params:
            update_data["title"] = params["title"]
        if "description" in params:
            update_data["description"] = params["description"]
        if "status" in params:
            update_data["status"] = params["status"]
        
        result = await todo_client.update_todo(todo_id, **update_data)
        return result
    
    except Exception as e:
        logger.error(f"Error updating todo: {str(e)}")
        return {"status": "error", "message": str(e)}


@app.post("/tools/delete_todo/call")
async def delete_todo_tool(request: Dict[str, Any]):
    """Delete a todo via MCP tool."""
    try:
        params = request.get("params", {})
        todo_id = params.get("id")
        
        if not todo_id:
            return {"status": "error", "message": "ID is required"}
        
        result = await todo_client.delete_todo(todo_id)
        return result
    
    except Exception as e:
        logger.error(f"Error deleting todo: {str(e)}")
        return {"status": "error", "message": str(e)}


if __name__ == "__main__":
    import uvicorn
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8002))
    logger.info(f"Starting MCP Server on {host}:{port}")
    uvicorn.run(app, host=host, port=port, log_level=os.getenv("LOG_LEVEL", "info").lower())
