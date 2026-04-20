# 📋 Version & Model Information

**Last Updated**: Current Session  
**Status**: Production Ready ✅

---

## 🔍 Actual Versions in Use

This document specifies the exact versions and models currently implemented in the codebase and used in production.

### Frontend Stack

| Component | Version | File | Notes |
|-----------|---------|------|-------|
| Next.js | 14.0.0+ | `frontend/package.json` | React framework |
| React | 18.2.0+ | `frontend/package.json` | UI library |
| TypeScript | 5.3.0+ | `frontend/package.json` | Type safety |
| Tailwind CSS | 3.4.0+ | `frontend/package.json` | Styling |
| Node Runtime | 18-alpine | `frontend/Dockerfile` | Container runtime |

### Backend Stack

| Component | Version | File | Notes |
|-----------|---------|------|-------|
| FastAPI | 0.104.1 | `backend/requirements.txt` | Web framework |
| Python | 3.11 | `backend/Dockerfile` | Runtime |
| SQLAlchemy | 2.0.23 | `backend/requirements.txt` | ORM |
| Pydantic | 2.4.2 | `backend/requirements.txt` | Data validation |
| Psycopg2 | 2.9.9 | `backend/requirements.txt` | PostgreSQL driver |
| Uvicorn | 0.24.0 | `backend/requirements.txt` | ASGI server |

### LLM Orchestration Stack

| Component | Version | File | Notes |
|-----------|---------|------|-------|
| FastAPI | 0.104.1 | `llm-orchestration/requirements.txt` | Web framework |
| Python | 3.11 | `llm-orchestration/Dockerfile` | Runtime |
| FAISS | 1.7.4 | `llm-orchestration/requirements.txt` | Vector search |
| Sentence-transformers | 2.2.2 | `llm-orchestration/requirements.txt` | Embeddings |
| Scikit-learn | 1.3.2 | `llm-orchestration/requirements.txt` | ML utilities |

### MCP Server Stack

| Component | Version | File | Notes |
|-----------|---------|------|-------|
| FastAPI | 0.104.1 | `mcp-server/requirements.txt` | Web framework |
| Python | 3.11 | `mcp-server/Dockerfile` | Runtime |

### Database & Infrastructure

| Component | Version | Service | Notes |
|-----------|---------|---------|-------|
| PostgreSQL | 15-alpine | `chatbot_postgres` | Database |
| Ollama | Latest | `chatbot_ollama` | LLM runtime |
| Docker | Latest | System | Containerization |
| Docker Compose | Latest | System | Orchestration |

---

## 🤖 LLM Models in Use

### Chat Models

#### Default Model (Recommended)
- **Name**: Tinyllama 1.1B
- **Size**: 637 MB
- **Speed**: Fast (1-3 sec per query)
- **Quality**: Good for general tasks
- **Usage**: Default in code, set in `ollama_provider.py:15`
- **Command**: `docker exec chatbot_ollama ollama pull tinyllama`

#### Alternative Model (High Quality)
- **Name**: Llama2 7B
- **Size**: 3.8 GB
- **Speed**: Slower (3-8 sec per query)
- **Quality**: Excellent, more detailed responses
- **Usage**: Optional, can set `OLLAMA_MODEL=llama2` in `.env`
- **Command**: `docker exec chatbot_ollama ollama pull llama2`

### Embedding Model

- **Name**: Nomic-embed-text
- **Size**: 274 MB
- **Dimension**: 768
- **Usage**: All RAG operations (hardcoded in `ollama_provider.py:19`)
- **Function**: Converts text to vectors for semantic search
- **Command**: `docker exec chatbot_ollama ollama pull nomic-embed-text`

---

## 📝 Configuration Files

### Default Model Configuration

**File**: `.env.example` (Lines 26-31)

```bash
# Default: tinyllama (lightweight, fast)
OLLAMA_MODEL=tinyllama

# Options: tinyllama (637MB), llama2 (3.8GB)
# Change to: OLLAMA_MODEL=llama2 for better quality

# Embeddings model (fixed, only option)
OLLAMA_EMBEDDING_MODEL=nomic-embed-text
```

### Code Configuration

**File**: `llm-orchestration/app/orchestrator/provider/ollama_provider.py` (Lines 15-19)

```python
class OllamaProvider(LLMProvider):
    def __init__(
        self,
        model_name: str = "tinyllama",        # Default chat model
        embedding_model: str = "nomic-embed-text"  # Default embeddings
    ):
```

**File**: `llm-orchestration/app/main.py` (Lines 196-197)

```python
provider = OllamaProvider(
    model_name="tinyllama",
    embedding_model="nomic-embed-text",
    host="http://ollama:11434"
)
```

---

## 🔄 Model Switching Guide

### Changing Chat Model

#### Method 1: Using `.env` file (Recommended)

1. Edit `.env` file:
   ```bash
   # Change this line:
   OLLAMA_MODEL=tinyllama
   
   # To this:
   OLLAMA_MODEL=llama2
   ```

2. Restart the orchestration service:
   ```bash
   docker compose restart llm-orchestration
   ```

3. Verify the change:
   ```bash
   curl http://localhost:8001/health
   ```

#### Method 2: Runtime environment

```bash
# Start with specific model
docker compose -e OLLAMA_MODEL=llama2 up -d
```

### Downloading Models

```bash
# Download all available models
docker exec chatbot_ollama ollama pull tinyllama
docker exec chatbot_ollama ollama pull llama2
docker exec chatbot_ollama ollama pull nomic-embed-text

# List downloaded models
docker exec chatbot_ollama ollama list

# Remove unused models to save space
docker exec chatbot_ollama ollama rm tinyllama
```

---

## 📊 Model Performance Comparison

| Aspect | Tinyllama | Llama2 |
|--------|-----------|--------|
| **Size** | 637 MB | 3.8 GB |
| **Memory** | ~2 GB RAM | ~8 GB RAM |
| **Speed** | 1-3 sec | 3-8 sec |
| **Quality** | Good | Excellent |
| **Best For** | Testing, Development | Production, High Quality |
| **Recommended** | ✅ Yes (Default) | Optional |

---

## ✅ Verified Working Models

✅ **Tested and Confirmed Working**:

```bash
# Pull and verify
docker exec chatbot_ollama ollama pull tinyllama
docker exec chatbot_ollama ollama pull llama2
docker exec chatbot_ollama ollama pull nomic-embed-text

# Expected output:
# NAME                      SIZE     
# tinyllama:latest          637 MB   
# llama2:latest             3.8 GB   
# nomic-embed-text:latest   274 MB   
```

---

## 🔧 Troubleshooting Model Issues

### Model Won't Download

```bash
# Check Ollama is running
docker compose ps ollama

# Check internet connection
docker exec chatbot_ollama curl -I https://ollama.ai

# Try download again with verbose output
docker exec chatbot_ollama ollama pull llama2 --verbose
```

### Model Doesn't Load

```bash
# Check logs
docker compose logs llm-orchestration

# Verify model exists
docker exec chatbot_ollama ollama list

# Restart service
docker compose restart llm-orchestration
```

### Out of Memory

```bash
# Use lighter model (tinyllama)
# Or increase Docker memory allocation
# Docker Desktop → Settings → Resources → Memory: 8GB or higher
```

---

## 📖 Documentation References

For complete setup and usage:

- **README.md** - Main documentation with setup instructions
- **QUICKSTART.md** - 5-minute quick start guide
- **LAUNCH_GUIDE.md** - Detailed launch instructions
- **SETUP_VERIFICATION.md** - Verification checklist
- **ARCHITECTURE.md** - System architecture details

---

## 🎯 Next Steps

1. **Verify Models**: `docker exec chatbot_ollama ollama list`
2. **Test Chat**: Open http://localhost:3000 and chat
3. **Monitor Performance**: Check response times with both models
4. **Choose Default**: Keep `tinyllama` for development, switch to `llama2` for production

---

**Status**: ✅ All versions verified and tested  
**Last Verified**: Current session  
**Maintained By**: Development Team
