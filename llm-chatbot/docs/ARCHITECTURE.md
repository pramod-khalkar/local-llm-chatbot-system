# Architecture & Design Documentation

## System Architecture

### High-Level Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     Client Layer                            │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  Next.js Frontend (React + TypeScript)              │   │
│  │  - Chat Interface Component                         │   │
│  │  - Voice Input (Web Speech API)                     │   │
│  │  - Message List & History                          │   │
│  │  - Settings & Configuration                        │   │
│  └────────────────┬──────────────────────────────────┘   │
└─────────────────────┼────────────────────────────────────────┘
                      │ REST API / WebSocket
┌─────────────────────┼────────────────────────────────────────┐
│              API Gateway Layer                              │
│  ┌────────────────▼──────────────────────────────────┐     │
│  │  FastAPI Backend (Port 8000)                       │     │
│  │  - Chat Endpoints (/api/chat/*)                   │     │
│  │  - RAG Endpoints (/api/rag/*)                     │     │
│  │  - Speech Endpoints (/api/speech/*)               │     │
│  │  - Message Storage                                 │     │
│  │  - Session Management                             │     │
│  └──────────────────┬───────────────────────────────┘     │
└─────────────────────┼────────────────────────────────────────┘
                      │ REST API
┌─────────────────────┼────────────────────────────────────────┐
│           Orchestration Layer                               │
│  ┌────────────────▼──────────────────────────────────┐     │
│  │  LLM Orchestration Service (Port 8001)            │     │
│  │                                                    │     │
│  │  ┌─────────────────────────────────────────┐     │     │
│  │  │ Query Router                             │     │     │
│  │  │ - Intent Detection                       │     │     │
│  │  │ - Route to: Chat / RAG / Tools          │     │     │
│  │  └─────────────────────────────────────────┘     │     │
│  │                                                    │     │
│  │  ┌─────────────────────────────────────────┐     │     │
│  │  │ LLM Provider Abstraction                │     │     │
│  │  │ - Base Provider (ABC)                   │     │     │
│  │  │ - OllamaProvider (local)                │     │     │
│  │  │ - OpenAIProvider (cloud-ready)          │     │     │
│  │  └─────────────────────────────────────────┘     │     │
│  │                                                    │     │
│  │  ┌─────────────────────────────────────────┐     │     │
│  │  │ RAG Pipeline                            │     │     │
│  │  │ - Document Chunking                     │     │     │
│  │  │ - Embedding Generation                  │     │     │
│  │  │ - Semantic Search                       │     │     │
│  │  └─────────────────────────────────────────┘     │     │
│  │                                                    │     │
│  │  ┌─────────────────────────────────────────┐     │     │
│  │  │ Tool Executor (MCP Integration)         │     │     │
│  │  │ - Tool Detection                        │     │     │
│  │  │ - Tool Execution                        │     │     │
│  │  └─────────────────────────────────────────┘     │     │
│  └──────────┬──────────────────┬────────────┬──────┘     │
└─────────────┼──────────────────┼────────────┼──────────────┘
              │                  │            │
        ┌─────▼─────┐   ┌────────▼─────┐  ┌──▼──────┐
        │   Ollama   │   │    FAISS     │  │   MCP   │
        │  (LLM)     │   │ (Vector DB)  │  │ Server  │
        │ Port:11434 │   │ Port: mem    │  │ Port:802│
        └────────────┘   └──────────────┘  └─────────┘
        
        ┌────────────────────────┐
        │   PostgreSQL           │
        │   (Chat History)       │
        │   Port: 5432           │
        └────────────────────────┘
```

## Component Details

### 1. Frontend (Next.js)

**Purpose**: User interface and interaction layer

**Key Components**:
- `ChatInterface`: Main chat UI container
- `MessageList`: Displays chat messages
- `VoiceInput`: Voice recording interface
- `MessageComposer`: Text input area

**Services**:
- `api.ts`: REST API client for backend communication

**Hooks**:
- `useChat`: Chat state management and API calls
- `useVoice`: Voice recognition and synthesis

**Key Features**:
- Real-time message streaming
- Voice input/output support
- Responsive design with Tailwind CSS
- Error handling and loading states

### 2. Backend API (FastAPI)

**Purpose**: REST API endpoints for chat, RAG, and speech

**Structure**:
```
backend/
├── app/
│   ├── main.py           # FastAPI app entry point
│   ├── api/
│   │   ├── chat.py       # Chat endpoints
│   │   ├── rag.py        # RAG search endpoints
│   │   └── speech.py     # Speech-to-text endpoints
│   ├── models/
│   │   ├── database.py   # SQLAlchemy session config
│   │   ├── orm_models.py # Database models
│   │   └── schemas.py    # Pydantic schemas
│   ├── config/
│   │   └── settings.py   # Configuration management
│   ├── services/         # Business logic layer (optional)
│   └── utils/
│       └── logger.py     # Logging configuration
```

**Key Endpoints**:
- `POST /api/chat/sessions` - Create new chat session
- `POST /api/chat/message` - Send message and get response
- `GET /api/chat/sessions/{id}/messages` - Get chat history
- `POST /api/rag/search` - Search documents
- `POST /api/rag/index-documents` - Index new documents
- `POST /api/speech/to-text` - Convert speech to text

**Database Models**:
- `User` - User information
- `ChatSession` - Chat session metadata
- `ChatMessage` - Individual messages
- `DocumentChunk` - RAG document chunks
- `QueryLog` - Query analytics

### 3. LLM Orchestration Service (FastAPI)

**Purpose**: Route queries and coordinate LLM, RAG, and tool execution

**Structure**:
```
llm-orchestration/
├── app/
│   ├── main.py                    # FastAPI app
│   ├── orchestrator/
│   │   ├── query_router.py        # Intent detection
│   │   ├── provider/
│   │   │   ├── base.py            # Abstract LLM provider
│   │   │   ├── ollama_provider.py # Ollama implementation
│   │   │   └── openai_provider.py # OpenAI implementation (template)
│   │   ├── rag/
│   │   │   ├── faiss_handler.py  # FAISS operations
│   │   │   └── embeddings.py      # Text processing & chunking
│   │   └── mcp/
│   │       └── mcp_handler.py     # MCP tool integration
│   └── models/
│       └── schemas.py             # Pydantic schemas
```

**Key Features**:

1. **Query Router**
   - Detects query intent (chat/rag/tool)
   - Implements confidence scoring
   - Supports extensible routing rules

2. **LLM Provider Abstraction**
   - Base class: `LLMProvider`
   - Implementations: `OllamaProvider`, `OpenAIProvider`
   - Easy provider swapping via environment variable

3. **RAG Pipeline**
   - Text chunking with overlap
   - Embedding generation
   - FAISS vector search
   - Automatic indexing

4. **MCP Integration**
   - Tool discovery
   - Tool execution
   - Result formatting

**Key Endpoints**:
- `POST /api/orchestrator/chat` - Orchestrate query
- `POST /api/rag/search` - RAG search
- `POST /api/rag/index` - Index documents
- `GET /api/stats` - Service statistics

### 4. MCP Server

**Purpose**: Manage and execute tools (todo manager, etc.)

**Tools Supported**:
- `create_todo` - Create new task
- `list_todos` - List all tasks
- `complete_todo` - Mark task complete
- `update_todo` - Modify task
- `delete_todo` - Remove task

**Data Storage**: In-memory (can be extended to database)

### 5. Databases

**PostgreSQL**:
- Persistent chat history
- User data
- Query logs
- Production-ready

**FAISS**:
- Vector indexing
- Document chunks
- Embeddings
- Fast semantic search

**Ollama**:
- Model inference
- Embedding generation
- Local execution

## Design Patterns

### 1. Provider Pattern (LLM Abstraction)
```python
# Base class
class LLMProvider(ABC):
    async def generate(self, prompt: str) -> str:
        pass

# Implementations
class OllamaProvider(LLMProvider):
    async def generate(self, prompt: str) -> str:
        # Ollama-specific logic
        
class OpenAIProvider(LLMProvider):
    async def generate(self, prompt: str) -> str:
        # OpenAI-specific logic
```

**Benefit**: Easy provider swapping without code changes

### 2. Service-Oriented Architecture
- Separate services for different concerns
- REST API communication
- Independent scaling and deployment

### 3. Query Routing Pattern
```
User Input
    ↓
Query Router (Intent Detection)
    ↓
Route Decision (chat/rag/tool)
    ↓
Execute Appropriate Handler
    ↓
Format Response
```

### 4. RAG Pipeline
```
Documents
    ↓
Text Chunking
    ↓
Embedding Generation
    ↓
Vector Store (FAISS)
    ↓
Query
    ↓
Semantic Search
    ↓
Context Augmentation
```

## Data Flow Examples

### Example 1: Simple Chat Query
```
1. User: "What is AI?"
2. Frontend → Backend Chat API
3. Backend → Orchestration Service
4. Query Router: Type = "chat", Confidence = 0.95
5. LLM Provider (Ollama): Generate response
6. Response → Backend → Frontend
7. Display message
```

### Example 2: RAG Query
```
1. User: "What does my document say about revenue?"
2. Frontend → Backend Chat API
3. Backend → Orchestration Service
4. Query Router: Type = "hybrid", RAG = True
5. RAG Pipeline:
   a. Embed user query
   b. FAISS search
   c. Retrieve top-k documents
6. LLM Provider: Generate response with context
7. Response with sources → Backend → Frontend
8. Display message + sources
```

### Example 3: Tool Query
```
1. User: "Create a todo: finish project"
2. Frontend → Backend Chat API
3. Backend → Orchestration Service
4. Query Router: Type = "tool", Tool = "create_todo"
5. MCP Handler: Call create_todo endpoint
6. Tool Result + LLM Response → Backend → Frontend
7. Display confirmation
```

## Security Considerations

1. **API Security**
   - CORS configuration
   - Input validation (Pydantic)
   - Error handling (no sensitive info in errors)

2. **Database Security**
   - Password authentication
   - Connection pooling
   - SQL injection prevention (SQLAlchemy)

3. **LLM Security**
   - Input sanitization
   - Output validation
   - Rate limiting

4. **Tool Execution**
   - Tool whitelisting
   - Parameter validation
   - Sandboxing (consider for production)

## Scalability Considerations

1. **Horizontal Scaling**
   - Stateless services (use Redis for sessions if needed)
   - Load balancer in front of APIs
   - Database connection pooling

2. **Caching**
   - Frontend: Cache responses
   - Backend: Cache embeddings
   - RAG: Cache search results

3. **Async Processing**
   - FastAPI async endpoints
   - Task queues for long-running jobs (Celery/RQ)
   - WebSocket for streaming

4. **Database Optimization**
   - Indexing on frequently queried columns
   - Connection pooling
   - Read replicas for scaling

## Development Workflow

1. **Local Development**
   - Use Docker Compose for full stack
   - Enable auto-reload on file changes
   - Use logging for debugging

2. **Testing**
   - Unit tests for business logic
   - Integration tests for APIs
   - End-to-end tests for workflows

3. **Deployment**
   - Docker images for each service
   - Environment-specific configurations
   - CI/CD pipeline (GitHub Actions)

## Future Enhancements

1. **Advanced RAG**
   - Reranking models
   - Query decomposition
   - Multi-modal embeddings

2. **Tool Framework**
   - Custom tool creation
   - Tool chaining
   - Async tool execution

3. **Authentication**
   - User authentication
   - API keys
   - Role-based access control

4. **Monitoring**
   - Prometheus metrics
   - Grafana dashboards
   - Alert systems

5. **Observability**
   - Distributed tracing
   - Performance profiling
   - Error tracking
