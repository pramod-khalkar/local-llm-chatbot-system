# 📁 Project Structure

## Complete Directory Layout

```
llm-chatbot/
│
├── README.md                          # Main documentation (START HERE!)
├── QUICKSTART.md                      # 5-minute quick start guide
├── .env.example                       # Environment variables template
├── .gitignore                         # Git ignore rules
├── docker-compose.yml                 # Docker Compose orchestration
│
├── frontend/                          # Next.js Frontend Application
│   ├── Dockerfile                     # Frontend container
│   ├── package.json                   # Dependencies
│   ├── next.config.js                 # Next.js configuration
│   ├── tsconfig.json                  # TypeScript configuration
│   ├── tailwind.config.js             # Tailwind CSS configuration
│   ├── postcss.config.js              # PostCSS configuration
│   └── src/
│       ├── app/
│       │   ├── layout.tsx             # Root layout
│       │   └── page.tsx               # Home page
│       ├── components/
│       │   ├── ChatInterface/
│       │   │   └── index.tsx          # Main chat interface
│       │   ├── MessageList/
│       │   │   └── index.tsx          # Message display component
│       │   └── VoiceInput/
│       │       └── index.tsx          # Voice input component
│       ├── hooks/
│       │   ├── useChat.ts             # Chat state management
│       │   └── useVoice.ts            # Voice recognition hooks
│       ├── services/
│       │   └── api.ts                 # API client service
│       └── styles/
│           └── globals.css            # Global styles
│
├── backend/                           # FastAPI Backend Service
│   ├── Dockerfile                     # Backend container
│   ├── requirements.txt               # Python dependencies
│   └── app/
│       ├── main.py                    # FastAPI application entry
│       ├── api/
│       │   ├── __init__.py
│       │   ├── chat.py                # Chat endpoints
│       │   ├── rag.py                 # RAG endpoints
│       │   └── speech.py              # Speech-to-text endpoints
│       ├── models/
│       │   ├── __init__.py
│       │   ├── database.py            # SQLAlchemy setup
│       │   ├── orm_models.py          # Database models
│       │   └── schemas.py             # Pydantic schemas
│       ├── config/
│       │   ├── __init__.py
│       │   └── settings.py            # Configuration management
│       ├── services/
│       │   └── __init__.py            # Business logic layer
│       └── utils/
│           ├── __init__.py
│           └── logger.py              # Logging setup
│
├── llm-orchestration/                 # LLM Orchestration Service
│   ├── Dockerfile                     # Orchestration container
│   ├── requirements.txt               # Python dependencies
│   └── app/
│       ├── main.py                    # FastAPI application entry
│       ├── orchestrator/
│       │   ├── __init__.py
│       │   ├── query_router.py        # Intent detection & routing
│       │   ├── provider/              # LLM Provider abstraction
│       │   │   ├── __init__.py
│       │   │   ├── base.py            # Abstract base provider
│       │   │   ├── ollama_provider.py # Ollama implementation
│       │   │   └── openai_provider.py # OpenAI template
│       │   ├── rag/                   # RAG pipeline
│       │   │   ├── __init__.py
│       │   │   ├── faiss_handler.py   # FAISS vector DB
│       │   │   └── embeddings.py      # Text chunking & embedding
│       │   └── mcp/                   # MCP tool integration
│       │       ├── __init__.py
│       │       └── mcp_handler.py     # MCP operations
│       └── models/
│           ├── __init__.py
│           └── schemas.py             # Pydantic schemas
│
├── mcp-server/                        # MCP Todo Task Manager
│   ├── Dockerfile                     # MCP container
│   ├── app.py                         # FastAPI MCP server
│   └── requirements.txt               # Python dependencies
│
├── docs/                              # Documentation
│   ├── ARCHITECTURE.md                # Detailed architecture
│   └── PROJECT_STRUCTURE.md           # This file
│
└── [Data Volumes - Created at runtime]
    ├── postgres_data/                 # PostgreSQL persistence
    ├── ollama_data/                   # Ollama models cache
    └── faiss_data/                    # FAISS indexes
```

## Key Files & Their Purpose

### Root Level
- **README.md** - Complete documentation with setup, usage, and API docs
- **QUICKSTART.md** - 5-minute quick start guide
- **docker-compose.yml** - Orchestrates all services
- **.env.example** - Environment variable template

### Frontend (Next.js)
- **src/app/page.tsx** - Main chat page entry point
- **src/components/ChatInterface** - Main chat UI container
- **src/hooks/useChat.ts** - Chat logic and state management
- **src/services/api.ts** - Backend API client

### Backend (FastAPI)
- **app/main.py** - FastAPI application setup and middleware
- **app/api/chat.py** - Chat creation, messaging endpoints
- **app/models/orm_models.py** - SQLAlchemy database models
- **app/config/settings.py** - Environment-based configuration

### LLM Orchestration
- **app/main.py** - Orchestration service entry point
- **app/orchestrator/query_router.py** - Intent detection
- **app/orchestrator/provider/base.py** - LLM abstraction layer
- **app/orchestrator/rag/faiss_handler.py** - Vector search

### MCP Server
- **app.py** - Standalone FastAPI todo manager

## File Dependencies

### Frontend Dependencies
```
page.tsx
  ↓ uses
ChatInterface → useChat hook → api service → Backend APIs
    ↓          ↓
MessageList  VoiceInput (useVoice hook)
```

### Backend Dependencies
```
main.py (FastAPI app)
  ├── api/chat.py → models/orm_models.py → database.py
  ├── api/rag.py → calls Orchestration service
  └── api/speech.py → placeholder
```

### Orchestration Dependencies
```
main.py
  ├── query_router.py (routing decision)
  ├── orchestrator/provider/
  │   ├── base.py (abstraction)
  │   └── ollama_provider.py (Ollama calls)
  ├── orchestrator/rag/
  │   ├── faiss_handler.py (vector search)
  │   └── embeddings.py (chunking)
  └── orchestrator/mcp/
      └── mcp_handler.py (tool calls)
```

## Environment Files

### Root .env
- Database connection
- LLM configuration
- Service ports
- CORS settings

### Docker Compose
- Service definitions
- Port mappings
- Environment injection
- Volume management

## Data Flow Through Files

### Chat Message Flow
```
Frontend/page.tsx
    ↓ (message input)
ChatInterface component
    ↓ (handleSendMessage)
useChat hook
    ↓ (chatService.sendMessage)
api.ts (axios client)
    ↓ HTTP POST
backend/app/main.py
    ↓ (includes chat router)
backend/app/api/chat.py (send_message endpoint)
    ↓ (stores user message, calls orchestration)
llm-orchestration/app/main.py
    ↓ (/api/orchestrator/chat endpoint)
query_router.py (route decision)
    ↓ (route to chat/rag/tools)
provider/ollama_provider.py (LLM call)
    ↓ (gets response)
Response returned to frontend
    ↓
Frontend displays message
```

## Configuration Files

- **frontend/next.config.js** - Next.js build settings
- **frontend/tsconfig.json** - TypeScript configuration
- **frontend/tailwind.config.js** - Tailwind CSS theming
- **backend/app/config/settings.py** - Backend settings
- **llm-orchestration/app/orchestrator/query_router.py** - Routing rules
- **docker-compose.yml** - Service orchestration
- **.env** - Runtime configuration

## How to Add New Features

### Adding a New API Endpoint
1. Create handler in `backend/app/api/new_feature.py`
2. Add Pydantic schema to `backend/app/models/schemas.py`
3. Include router in `backend/app/main.py`
4. Call from frontend `src/services/api.ts`

### Adding a New LLM Provider
1. Create class in `llm-orchestration/app/orchestrator/provider/new_provider.py`
2. Extend `LLMProvider` base class
3. Update `.env` file
4. No other code changes needed!

### Adding a New MCP Tool
1. Add endpoint to `mcp-server/app.py`
2. Update tool registry in MCP handler
3. Add routing rules in `llm-orchestration/orchestrator/query_router.py`

## Testing Key Files

- **Frontend**: `src/services/api.ts` - Mock API calls
- **Backend**: `app/api/chat.py` - Test endpoints with curl
- **Orchestration**: `app/main.py` - Test routing logic
- **MCP**: `mcp-server/app.py` - Test tool endpoints

---

**Note**: This structure is designed for scalability and easy provider swapping. Keep services loosely coupled for maximum flexibility!
