from fastapi import FastAPI, HTTPException, Depends, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
import os
import asyncio
import json
from typing import List, Optional

# Configure logging
logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
logger = logging.getLogger(__name__)

# Import orchestrator components
from app.orchestrator.provider.base import ProviderFactory
from app.orchestrator.provider.ollama_provider import OllamaProvider
from app.orchestrator.query_router import QueryRouter
from app.orchestrator.rag.faiss_handler import FAISSVectorStore
from app.orchestrator.rag.embeddings import EmbeddingsPipeline
from app.orchestrator.mcp.mcp_handler import MCPHandler
from app.models.schemas import OrchestrationQuery, OrchestrationResponse, RagSearchRequest, RagIndexRequest

# Initialize components
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager."""
    logger.info("Initializing LLM Orchestration Service...")
    
    # Initialize provider
    global llm_provider, query_router, rag_store, embeddings_pipeline, mcp_handler
    
    ollama_host = os.getenv("OLLAMA_HOST", "http://localhost:11434")
    llm_provider = OllamaProvider(
        host=ollama_host,
        embedding_model=os.getenv("EMBEDDING_MODEL", "nomic-embed-text")
    )
    
    query_router = QueryRouter()
    rag_store = FAISSVectorStore(index_path=os.getenv("FAISS_INDEX_PATH", "/data/faiss_index"), dimension=768)
    embeddings_pipeline = EmbeddingsPipeline(
        chunk_size=int(os.getenv("CHUNK_SIZE", 512)),
        chunk_overlap=int(os.getenv("CHUNK_OVERLAP", 50))
    )
    mcp_handler = MCPHandler(
        host=os.getenv("MCP_SERVER_HOST", "localhost"),
        port=int(os.getenv("MCP_SERVER_PORT", 8002))
    )
    
    logger.info("✓ Orchestration service initialized")
    yield
    logger.info("Orchestration service shutting down...")


# Create app
app = FastAPI(
    title="LLM Orchestration Service",
    description="Orchestration layer for LLM, RAG, and tool integration",
    version="1.0.0",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global components (initialized in lifespan)
llm_provider = None
query_router = None
rag_store = None
embeddings_pipeline = None
mcp_handler = None


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "orchestration"}


@app.post("/api/orchestrator/chat", response_model=OrchestrationResponse)
async def orchestrate_chat(query: OrchestrationQuery) -> OrchestrationResponse:
    """Orchestrate chat with routing to RAG and tools."""
    try:
        logger.info(f"Orchestrating query: {query.query[:100]}...")
        
        # Route query
        logger.info("Step 1: Routing query...")
        routing = await query_router.route_query(query.query, query.context)
        logger.info(f"Step 1 done: query_type={routing.query_type}, tool_name={routing.tool_name}")
        
        # Get LLM response
        logger.info("Step 2: Generating LLM response...")
        response = await llm_provider.generate(
            prompt=query.query,
            context=query.context
        )
        logger.info("Step 2 done: LLM response generated")
        
        sources = []
        tool_calls = []
        llm_response = response.get("response", "")
        
        # If RAG required, search documents
        if routing.rag_required and query.use_rag:
            logger.info(f"Step 3: RAG search triggered for query: {query.query[:50]}...")
            try:
                embedding = await llm_provider.embed_text(query.query)
                logger.info(f"Step 3a: Embedding generated, dimensions={len(embedding) if embedding else 0}")
                logger.info(f"Step 3b: Index stats before search: {rag_store.get_stats()}")
                results = rag_store.search(embedding, k=5, threshold=0.0)
                logger.info(f"Step 3c: RAG search returned {len(results)} results")
                for i, r in enumerate(results):
                    logger.info(f"Step 3d: Result {i}: score={r.get('score')}, content_len={len(r.get('content', ''))}")
                sources = [r.get("content", "")[:100] for r in results]
                logger.info(f"Step 3 done: Found {len(sources)} RAG sources")
            except Exception as e:
                logger.error(f"Step 3 Error: {str(e)}", exc_info=True)
                sources = []
        
        # If tool required, call appropriate MCP tool
        if routing.query_type == "tool" and query.use_tools:
            logger.info(f"Step 4: Tool call triggered for tool: {routing.tool_name}, action: {routing.tool_action}")
            try:
                # For todo-related queries, dispatch based on action
                if routing.tool_name == "todo":
                    tool_action = routing.tool_action or "list"
                    logger.info(f"Step 4a: Todo action detected: {tool_action}")
                    
                    if tool_action == "create":
                        # Extract title and description from query using LLM
                        logger.info("Step 4b: Extracting todo details from query...")
                        extraction_prompt = f"""Extract the todo task details from this request:
"{query.query}"

Return ONLY a JSON object with:
{{"title": "task title", "description": "optional description"}}

Example: {{"title": "Buy groceries", "description": "milk, eggs, bread"}}"""
                        
                        extraction_response = await llm_provider.generate(prompt=extraction_prompt)
                        try:
                            extracted = json.loads(extraction_response.get("response", "{}"))
                            title = extracted.get("title", "New Task")
                            description = extracted.get("description", "")
                            logger.info(f"Step 4c: Extracted - title='{title}', description='{description}'")
                            
                            tool_result = await asyncio.wait_for(
                                mcp_handler.create_todo(title, description),
                                timeout=600.0
                            )
                            logger.info(f"Step 4d: create_todo completed with status={tool_result.get('status')}")
                            tool_calls = ["create_todo"]
                            
                            if tool_result.get("status") == "success":
                                todo_data = tool_result.get("data", {})
                                todo_id = todo_data.get("id", "")
                                llm_response = f"✓ Todo created successfully!\n\nTitle: {title}\nID: {todo_id}\nDescription: {description}"
                                logger.info("Step 4e: Todo created successfully")
                            else:
                                error_msg = tool_result.get("message", "Unknown error")
                                llm_response = f"✗ Failed to create todo: {error_msg}"
                                logger.warning(f"Step 4e: Todo creation failed: {error_msg}")
                        except json.JSONDecodeError:
                            logger.warning("Failed to parse extraction response as JSON, using defaults")
                            title = query.query[:50]  # Use first 50 chars as title
                            tool_result = await asyncio.wait_for(
                                mcp_handler.create_todo(title, ""),
                                timeout=600.0
                            )
                            tool_calls = ["create_todo"]
                            if tool_result.get("status") == "success":
                                llm_response = f"✓ Todo created: {title}"
                            else:
                                llm_response = f"✗ Failed to create todo: {tool_result.get('message')}"
                    
                    elif tool_action == "complete":
                        # Extract todo ID/title to complete
                        logger.info("Step 4b: Extracting todo ID/title for completion...")
                        extraction_prompt = f"""Extract the todo ID or title from this completion request:
"{query.query}"

Return ONLY a JSON object with:
{{"todo_id": "id if mentioned", "todo_title": "title if mentioned"}}

Example: {{"todo_id": "1", "todo_title": ""}}"""
                        
                        extraction_response = await llm_provider.generate(prompt=extraction_prompt)
                        try:
                            extracted = json.loads(extraction_response.get("response", "{}"))
                            todo_id = extracted.get("todo_id")
                            todo_title = extracted.get("todo_title")
                            
                            if todo_id:
                                logger.info(f"Step 4c: Completing todo ID: {todo_id}")
                                tool_result = await asyncio.wait_for(
                                    mcp_handler.complete_todo(todo_id),
                                    timeout=600.0
                                )
                                tool_calls = ["complete_todo"]
                                
                                if tool_result.get("status") == "success":
                                    llm_response = f"✓ Todo marked as complete!"
                                    logger.info("Step 4d: Todo completed successfully")
                                else:
                                    llm_response = f"✗ Failed to complete todo: {tool_result.get('message')}"
                                    logger.warning(f"Step 4d: Failed to complete: {tool_result.get('message')}")
                            else:
                                llm_response = "⚠ Could not identify which todo to complete. Please specify the todo ID or title."
                                logger.warning("Step 4c: Could not extract todo ID/title")
                        except json.JSONDecodeError:
                            llm_response = "⚠ Could not parse todo details for completion"
                            logger.warning("Failed to parse completion extraction")
                    
                    else:  # list or default
                        logger.info("Step 4b: Calling list_todos tool...")
                        tool_result = await asyncio.wait_for(
                            mcp_handler.list_todos(),
                            timeout=600.0
                        )
                        logger.info(f"Step 4c: list_todos completed with status={tool_result.get('status')}")
                        tool_calls = ["list_todos"]
                        
                        if tool_result.get("status") == "success":
                            todos = tool_result.get("todos", [])
                            if todos:
                                todo_summary = f"You have {len(todos)} todo(s):\n\n"
                                for i, todo in enumerate(todos, 1):
                                    title = todo.get("title", "")
                                    status = todo.get("status", "")
                                    todo_id = todo.get("id", "")
                                    todo_summary += f"{i}. [{status}] {title} (ID: {todo_id})\n"
                                llm_response = todo_summary
                            else:
                                llm_response = "✓ You have no todos! Great job!"
                            logger.info(f"Step 4d: Todo list generated: {len(todos)} todos")
                        else:
                            error_msg = tool_result.get("message", "Unknown error")
                            llm_response = f"✗ Failed to list todos: {error_msg}"
                            logger.warning(f"Step 4d: Failed to list todos: {error_msg}")
            
            except asyncio.TimeoutError:
                logger.error("Step 4: Tool call timed out after 600 seconds")
                llm_response = "✗ Tool call timed out. Please try again."
            except Exception as e:
                logger.error(f"Step 4: Error calling MCP tool: {str(e)}", exc_info=True)
                llm_response = f"✗ Error: {str(e)}"
        
        logger.info("Returning orchestration response...")
        return OrchestrationResponse(
            response=llm_response,
            query_type=routing.query_type,
            sources=sources,
            tool_calls=tool_calls,
            tokens=response.get("tokens")
        )
    
    except Exception as e:
        logger.error(f"Error in orchestration: {str(e)}")
        raise HTTPException(status_code=500, detail="Orchestration failed")


@app.post("/api/rag/search")
async def rag_search(request: RagSearchRequest):
    """Search documents using RAG."""
    try:
        # Get embedding for query
        embedding = await llm_provider.embed_text(request.query)
        
        # Search FAISS
        results = rag_store.search(
            embedding,
            k=request.top_k,
            threshold=request.threshold
        )
        
        return {"results": results}
    
    except Exception as e:
        logger.error(f"Error in RAG search: {str(e)}")
        raise HTTPException(status_code=500, detail="RAG search failed")


@app.post("/api/rag/index")
async def index_documents(request: RagIndexRequest):
    """Index documents for RAG. Accepts JSON with document content."""
    try:
        documents = request.documents
        
        if not documents:
            raise ValueError("No documents provided")
        
        logger.info(f"Processing {len(documents)} documents for RAG indexing")
        
        # Chunk documents
        chunks = embeddings_pipeline.chunk_documents(documents)
        logger.info(f"Created {len(chunks)} chunks from documents")
        
        # Get embeddings for chunks
        chunk_texts = [c.get("content", "") for c in chunks]
        embeddings = await llm_provider.embed_batch(chunk_texts)
        logger.info(f"Generated {len(embeddings)} embeddings")
        
        # Add to FAISS
        metadata = [c.get("metadata", {}) for c in chunks]
        count = rag_store.add_documents(embeddings, chunk_texts, metadata)
        logger.info(f"Added {count} vectors to FAISS")
        
        # Get stats
        stats = rag_store.get_stats()
        
        return {
            "status": "success",
            "indexed_count": count,
            "total_vectors": stats.get("total_vectors", 0),
            "dimension": stats.get("dimension", 768),
            "message": f"Successfully indexed {count} document(s)"
        }
    
    except Exception as e:
        logger.error(f"Error indexing documents: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Document indexing failed: {str(e)}")


@app.get("/api/stats")
async def get_stats():
    """Get service statistics."""
    return {
        "rag_store": rag_store.get_stats() if rag_store else {},
        "routing": query_router.get_routing_stats() if query_router else {},
        "status": "running"
    }
