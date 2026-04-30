from fastapi import FastAPI, HTTPException, Depends, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
import os
import asyncio
import json
import time # Added import for time module
from typing import List, Optional

# Configure logging
logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
logger = logging.getLogger(__name__)

# Import orchestrator components
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

    # Initialize MCPHandler FIRST
    mcp_handler = MCPHandler(
        host=os.getenv("MCP_SERVER_HOST", "localhost"),
        port=int(os.getenv("MCP_SERVER_PORT", 8002))
    )
    logger.info(f"lifespan: mcp_handler initialized to = {mcp_handler}")
    if mcp_handler is None:
        raise RuntimeError("MCPHandler failed to initialize; it is None.")

    # Then initialize QueryRouter with the now-initialized mcp_handler
    query_router = QueryRouter(llm_provider=llm_provider, mcp_handler=mcp_handler)
    await query_router._fetch_tools() # Explicitly fetch tools after initialization

    rag_store = FAISSVectorStore(index_path=os.getenv("FAISS_INDEX_PATH", "/data/faiss_index"), dimension=768)
    embeddings_pipeline = EmbeddingsPipeline(
        chunk_size=int(os.getenv("CHUNK_SIZE", 512)),
        chunk_overlap=int(os.getenv("CHUNK_OVERLAP", 50))
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
    start_orchestration_time = time.time()
    try:
        logger.info(f"Orchestrating query: {query.query[:100]}...")

        # Route query
        start_routing_time = time.time()
        logger.info("Step 1: Routing query...")
        routing = await query_router.route_query(query.query, query.context)
        routing_duration = time.time() - start_routing_time
        logger.info(f"Step 1 done (took {routing_duration:.2f}s): query_type={routing.query_type}, tool_name={routing.tool_name}")

        # Get LLM response (initial or default)
        start_llm_gen_time = time.time()
        logger.info("Step 2: Generating initial LLM response...")
        response = await llm_provider.generate(
            prompt=query.query,
            context=query.context
        )
        llm_gen_duration = time.time() - start_llm_gen_time
        logger.info(f"Step 2 done (took {llm_gen_duration:.2f}s): LLM response generated")

        sources = []
        tool_calls = []
        llm_response = response.get("response", "")

        # If RAG required, search documents
        if routing.rag_required and query.use_rag:
            start_rag_time = time.time()
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
                rag_duration = time.time() - start_rag_time
                logger.info(f"Step 3 done (took {rag_duration:.2f}s): Found {len(sources)} RAG sources")
            except Exception as e:
                logger.error(f"Step 3 Error: {str(e)}", exc_info=True)
                sources = []

        # If tool required, call appropriate MCP tool
        if routing.query_type == "tool" and query.use_tools and routing.tool_name:
            start_tool_time = time.time()
            logger.info(f"Step 4: Tool call triggered for tool: {routing.tool_name}")
            tool_calls = [routing.tool_name] # Mark tool as called

            try:
                # Extract tool name and parameters
                tool_name = routing.tool_name
                tool_params = routing.tool_params if routing.tool_params is not None else {}

                tool_result = None
                if tool_name == "create_todo":
                    title = tool_params.get("title")
                    description = tool_params.get("description", "")
                    if not title:
                        llm_response = "✗ Missing title for todo creation."
                        logger.warning("Step 4: create_todo called without a title.")
                    else:
                        tool_result = await asyncio.wait_for(
                            mcp_handler.create_todo(title, description),
                            timeout=600.0
                        )
                        if tool_result and tool_result.get("status") == "success":
                            todo_data = tool_result.get("data", {})
                            todo_id = todo_data.get("id", "")
                            llm_response = f"✓ Todo created successfully!\n\nTitle: {title}\nID: {todo_id}\nDescription: {description}"
                            logger.info("Step 4: create_todo completed successfully.")
                        else:
                            error_msg = tool_result.get("message", "Unknown error")
                            llm_response = f"✗ Failed to create todo: {error_msg}"
                            logger.warning(f"Step 4: create_todo failed: {error_msg}")

                elif tool_name == "list_todos":
                    tool_result = await asyncio.wait_for(
                        mcp_handler.list_todos(),
                        timeout=600.0
                    )
                    if tool_result and tool_result.get("status") == "success":
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
                        logger.info("Step 4: list_todos completed successfully.")
                    else:
                        error_msg = tool_result.get("message", "Unknown error")
                        llm_response = f"✗ Failed to list todos: {error_msg}"
                        logger.warning(f"Step 4: list_todos failed: {error_msg}")

                elif tool_name == "complete_todo":
                    todo_id = tool_params.get("id")
                    if not todo_id:
                        llm_response = "✗ Missing todo ID for completion."
                        logger.warning("Step 4: complete_todo called without an ID.")
                    else:
                        tool_result = await asyncio.wait_for(
                            mcp_handler.complete_todo(todo_id),
                            timeout=600.0
                        )
                        if tool_result and tool_result.get("status") == "success":
                            llm_response = f"✓ Todo {todo_id} marked as complete!"
                            logger.info(f"Step 4: complete_todo for ID {todo_id} completed successfully.")
                        else:
                            error_msg = tool_result.get("message", "Unknown error")
                            llm_response = f"✗ Failed to complete todo {todo_id}: {error_msg}"
                            logger.warning(f"Step 4: complete_todo for ID {todo_id} failed: {error_msg}")
                else:
                    llm_response = f"⚠ Tool '{tool_name}' is not directly supported by this orchestrator for direct invocation."
                    logger.warning(f"Step 4: Unsupported tool '{tool_name}' invoked.")

                tool_duration = time.time() - start_tool_time
                logger.info(f"Step 4 done (took {tool_duration:.2f}s): Tool call for '{tool_name}' completed.")

            except asyncio.TimeoutError:
                logger.error("Step 4: Tool call timed out after 600 seconds")
                llm_response = "✗ Tool call timed out. Please try again."
            except Exception as e:
                logger.error(f"Step 4: Error calling MCP tool '{tool_name}': {str(e)}", exc_info=True)
                llm_response = f"✗ Error calling tool '{tool_name}': {str(e)}"

        total_orchestration_duration = time.time() - start_orchestration_time
        logger.info(f"Returning orchestration response (total duration: {total_orchestration_duration:.2f}s)...")
        return OrchestrationResponse(            response=llm_response,
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
