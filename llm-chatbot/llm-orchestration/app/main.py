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
from app.orchestrator.provider.openai_provider import OpenAIProvider
from app.orchestrator.provider.gemini_provider import GeminiProvider
from app.orchestrator.query_router import QueryRouter
from app.orchestrator.chatgpt_router import ChatGPTRouter
from app.orchestrator.gemini_router import GeminiRouter
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
    global llm_provider, query_router, chatgpt_router, rag_store, embeddings_pipeline, mcp_handler
    
    provider_type = os.getenv("LLM_PROVIDER", "ollama").lower()
    logger.info(f"Selected LLM provider: {provider_type}")
    
    if provider_type == "openai":
        openai_model = os.getenv("CHATGPT_MODEL", "gpt-3.5-turbo")
        llm_provider = OpenAIProvider(
            model_name=openai_model,
            temperature=float(os.getenv("TEMPERATURE", "0.7")),
            max_tokens=int(os.getenv("MAX_TOKENS", "2048"))
        )
        default_dimension = 1536
        logger.info(f"✓ OpenAI provider initialized with model: {openai_model}")
    elif provider_type == "gemini":
        gemini_model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
        llm_provider = GeminiProvider(
            model_name=gemini_model,
            temperature=float(os.getenv("TEMPERATURE", "0.7")),
            max_tokens=int(os.getenv("MAX_TOKENS", "2048"))
        )
        # models/gemini-embedding-001 is 768 dimensions
        default_dimension = 768
        logger.info(f"✓ Gemini provider initialized with model: {gemini_model}")
    else:
        ollama_host = os.getenv("OLLAMA_HOST", "http://ollama:11434")
        ollama_model = os.getenv("OLLAMA_MODEL", "tinyllama")
        llm_provider = OllamaProvider(
            model_name=ollama_model,
            host=ollama_host,
            embedding_model=os.getenv("OLLAMA_EMBEDDING_MODEL", "nomic-embed-text")
        )
        default_dimension = 768
        logger.info(f"✓ Ollama provider initialized with model: {ollama_model}")
    
    # Initialize standard query router (fallback)
    query_router = QueryRouter()
    
    # Initialize ChatGPT/Gemini router for routing and extraction
    use_chatgpt = os.getenv("USE_CHATGPT_ROUTING", "true").lower() == "true"
    if use_chatgpt:
        try:
            if provider_type == "gemini":
                from app.orchestrator.gemini_router import GeminiRouter
                gemini_model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
                chatgpt_router = GeminiRouter(model=gemini_model)
                logger.info(f"✓ Gemini router initialized successfully with model: {gemini_model}")

            else:
                chatgpt_model = os.getenv("CHATGPT_MODEL", "gpt-3.5-turbo")
                chatgpt_router = ChatGPTRouter(model=chatgpt_model)
                logger.info(f"✓ ChatGPT router initialized successfully with model: {chatgpt_model}")
        except Exception as e:
            logger.warning(f"Failed to initialize AI router: {e}. Will use fallback.")
            chatgpt_router = None
    else:
        chatgpt_router = None
        logger.info("AI routing disabled (USE_CHATGPT_ROUTING=false)")
    
    dimension = int(os.getenv("FAISS_DIMENSION", str(default_dimension)))
    rag_store = FAISSVectorStore(index_path=os.getenv("FAISS_INDEX_PATH", "/data/faiss_index"), dimension=dimension)
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
chatgpt_router = None
rag_store = None
embeddings_pipeline = None
mcp_handler = None


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "orchestration"}


@app.post("/api/orchestrator/chat", response_model=OrchestrationResponse)
async def orchestrate_chat(query: OrchestrationQuery) -> OrchestrationResponse:
    """Orchestrate chat with routing to RAG and tools using ChatGPT."""
    try:
        logger.info(f"Orchestrating query: {query.query[:100]}...")
        
        # Step 1: Route query using ChatGPT (if available) or fallback to TinyLlama
        logger.info("Step 1: Routing query...")
        if chatgpt_router:
            try:
                routing = await chatgpt_router.route_query(query.query, query.context)
                logger.info(f"ChatGPT routing: query_type={routing.get('query_type')}, tool_name={routing.get('tool_name')}, confidence={routing.get('confidence')}")
            except Exception as e:
                logger.warning(f"ChatGPT routing failed: {e}, falling back to TinyLlama")
                routing_obj = await query_router.route_query(query.query, query.context)
                routing = {
                    "query_type": routing_obj.query_type,
                    "tool_name": routing_obj.tool_name,
                    "tool_action": routing_obj.tool_action,
                    "rag_required": routing_obj.rag_required,
                    "confidence": 0.5
                }
        else:
            routing_obj = await query_router.route_query(query.query, query.context)
            routing = {
                "query_type": routing_obj.query_type,
                "tool_name": routing_obj.tool_name,
                "tool_action": routing_obj.tool_action,
                "rag_required": routing_obj.rag_required,
                "confidence": 0.5
            }
        
        logger.info(f"Step 1 done: query_type={routing.get('query_type')}, tool_name={routing.get('tool_name')}")
        
        # Initial response
        response = await llm_provider.generate(
            prompt=query.query,
            context=query.context
        )
        
        sources = []
        tool_calls = []
        llm_response = response.get("response", "")
        
        # Step 2: If RAG required, search documents
        if routing.get("rag_required") and query.use_rag:
            logger.info(f"Step 2: RAG search triggered for query: {query.query[:50]}...")
            try:
                embedding = await llm_provider.embed_text(query.query)
                logger.info(f"Step 2a: Embedding generated, dimensions={len(embedding) if embedding else 0}")
                logger.info(f"Step 2b: Index stats before search: {rag_store.get_stats()}")
                results = rag_store.search(embedding, k=5, threshold=0.0)
                logger.info(f"Step 2c: RAG search returned {len(results)} results")
                for i, r in enumerate(results):
                    logger.info(f"Step 2d: Result {i}: score={r.get('score')}, content_len={len(r.get('content', ''))}")
                sources = [r.get("content", "") for r in results if r.get("content")]
                logger.info(f"Step 2 done: Found {len(sources)} RAG sources")
                
                # Step 3: Use ChatGPT to refine response with RAG results
                if chatgpt_router and sources:
                    logger.info("Step 3: Refining response with RAG results using ChatGPT...")
                    try:
                        llm_response = await chatgpt_router.refine_with_rag_results(query.query, sources)
                        logger.info(f"Step 3 done: Response refined with RAG context (length: {len(llm_response)})")
                    except Exception as e:
                        logger.warning(f"ChatGPT RAG refinement failed: {e}, using original response")
                
            except Exception as e:
                logger.error(f"Step 2 Error: {str(e)}", exc_info=True)
                sources = []
        
        # Step 4: If tool required, call appropriate MCP tool
        if routing.get("query_type") == "tool" and query.use_tools:
            logger.info(f"Step 4: Tool call triggered for tool: {routing.get('tool_name')}, action: {routing.get('tool_action')}")
            try:
                # For todo-related queries, dispatch based on action
                if routing.get("tool_name") == "todo":
                    tool_action = routing.get("tool_action") or "list"
                    logger.info(f"Step 4a: Todo action detected: {tool_action}")
                    
                    if tool_action == "create":
                        # Extract title and description from query using ChatGPT
                        logger.info("Step 4b: Extracting todo details from query...")
                        if chatgpt_router:
                            try:
                                extracted = await chatgpt_router.extract_todo_params(query.query)
                                logger.info(f"Step 4c: ChatGPT extracted - title='{extracted['title']}', description='{extracted['description']}'")
                            except Exception as e:
                                logger.warning(f"ChatGPT extraction failed: {e}, using LLM extraction")
                                extraction_prompt = f"""Extract the todo task details from this request:
"{query.query}"

Return ONLY a JSON object with:
{{"title": "task title", "description": "optional description"}}

Example: {{"title": "Buy groceries", "description": "milk, eggs, bread"}}"""
                                
                                extraction_response = await llm_provider.generate(prompt=extraction_prompt)
                                try:
                                    extracted = json.loads(extraction_response.get("response", "{}"))
                                except json.JSONDecodeError:
                                    extracted = {"title": query.query[:50], "description": ""}
                        else:
                            extraction_prompt = f"""Extract the todo task details from this request:
"{query.query}"

Return ONLY a JSON object with:
{{"title": "task title", "description": "optional description"}}

Example: {{"title": "Buy groceries", "description": "milk, eggs, bread"}}"""
                            
                            extraction_response = await llm_provider.generate(prompt=extraction_prompt)
                            try:
                                extracted = json.loads(extraction_response.get("response", "{}"))
                            except json.JSONDecodeError:
                                extracted = {"title": query.query[:50], "description": ""}
                        
                        title = extracted.get("title", "New Task")
                        description = extracted.get("description", "")
                        
                        tool_result = await asyncio.wait_for(
                            mcp_handler.create_todo(title, description),
                            timeout=15.0
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
                    
                    elif tool_action == "complete":
                        # Extract todo ID/title to complete using ChatGPT
                        logger.info("Step 4b: Extracting todo ID/title for completion...")
                        if chatgpt_router:
                            try:
                                extracted = await chatgpt_router.extract_todo_id_for_completion(query.query)
                                logger.info(f"Step 4c: ChatGPT extracted - ID: {extracted['todo_id']}, Title: {extracted['todo_title']}")
                            except Exception as e:
                                logger.warning(f"ChatGPT extraction failed: {e}, using LLM extraction")
                                extraction_prompt = f"""Extract the todo ID or title from this completion request:
"{query.query}"

Return ONLY a JSON object with:
{{"todo_id": "id if mentioned", "todo_title": "title if mentioned"}}

Example: {{"todo_id": "1", "todo_title": ""}}"""
                                
                                extraction_response = await llm_provider.generate(prompt=extraction_prompt)
                                try:
                                    extracted = json.loads(extraction_response.get("response", "{}"))
                                except json.JSONDecodeError:
                                    extracted = {"todo_id": None, "todo_title": None}
                        else:
                            extraction_prompt = f"""Extract the todo ID or title from this completion request:
"{query.query}"

Return ONLY a JSON object with:
{{"todo_id": "id if mentioned", "todo_title": "title if mentioned"}}

Example: {{"todo_id": "1", "todo_title": ""}}"""
                            
                            extraction_response = await llm_provider.generate(prompt=extraction_prompt)
                            try:
                                extracted = json.loads(extraction_response.get("response", "{}"))
                            except json.JSONDecodeError:
                                extracted = {"todo_id": None, "todo_title": None}
                        
                        todo_id = extracted.get("todo_id")
                        
                        if todo_id:
                            logger.info(f"Step 4c: Completing todo ID: {todo_id}")
                            tool_result = await asyncio.wait_for(
                                mcp_handler.complete_todo(todo_id),
                                timeout=15.0
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
                    
                    else:  # list or default
                        logger.info("Step 4b: Calling list_todos tool...")
                        tool_result = await asyncio.wait_for(
                            mcp_handler.list_todos(),
                            timeout=15.0
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
                logger.error("Step 4: Tool call timed out after 15 seconds")
                llm_response = "✗ Tool call timed out. Please try again."
            except Exception as e:
                logger.error(f"Step 4: Error calling MCP tool: {str(e)}", exc_info=True)
                llm_response = f"✗ Error: {str(e)}"
        
        logger.info("Returning orchestration response...")
        return OrchestrationResponse(
            response=llm_response,
            query_type=routing.get("query_type"),
            sources=[s[:100] for s in sources],  # Limit source length for response
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
