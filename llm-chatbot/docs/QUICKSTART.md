# 🚀 Quick Start Guide

Get your LLM Chatbot running in **5 minutes**!

## Prerequisites
- Docker & Docker Compose
- 8GB+ RAM
- 20GB+ disk space

## Steps

### 1. Start Services (1 minute)
```bash
cd /Users/pramod/Documents/workspace/github/llm-chatbot

# Start all services
docker-compose up -d

# Verify services are running
docker-compose ps
```

**Expected Output:**
```
NAME                    STATUS
chatbot_frontend        Up
chatbot_backend         Up
chatbot_llm_orchestration   Up
chatbot_mcp_server      Up
chatbot_postgres        Up
chatbot_ollama          Up
```

### 2. Download Models (2-4 minutes)
```bash
# Pull Tinyllama model (lightweight, takes ~1-2 minutes)
docker exec chatbot_ollama ollama pull tinyllama

# Alternative: Pull Llama2 model (more powerful, takes ~2-3 minutes)
docker exec chatbot_ollama ollama pull llama2

# Pull embedding model (takes ~1-2 minutes)
docker exec chatbot_ollama ollama pull nomic-embed-text
```

**Note:** The application defaults to `tinyllama` for faster responses. Use `llama2` for more accurate results. Both work with the same embedding model.

### 3. Open Application (instant)
```bash
# Open in browser
open http://localhost:3000

# Or manually navigate to:
# http://localhost:3000
```

### 4. Start Chatting! 🎉
- Type a message and click "Send"
- Or use the 🎤 button for voice input
- Try enabling "📚 Use RAG" for document search
- Try enabling "🛠️ Use Tools" for todo creation

## Test Interactions

### Test 1: Basic Chat
```
User: "What is machine learning?"
Expected: AI-generated explanation
```

### Test 2: Tool Usage
```
User: "Create a todo: buy groceries"
Expected: Todo created, confirmation message
```

### Test 3: Voice Input
```
1. Click 🎤 button
2. Speak clearly: "Hello, how are you?"
3. Click 🎤 again to stop
4. Click "Send"
Expected: Transcribed text and response
```

## Troubleshooting

### Services won't start?
```bash
# Check logs
docker-compose logs

# Rebuild and start
docker-compose down -v
docker-compose build --no-cache
docker-compose up -d
```

### Models won't download?
```bash
# Check Ollama is running
docker exec chatbot_ollama ollama list

# Try pulling again
docker exec chatbot_ollama ollama pull llama2
```

### Can't access frontend?
```bash
# Check port 3000 is not in use
lsof -i :3000

# Check backend is running
curl http://localhost:8000/health
```

## API Endpoints

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000 (docs: /docs)
- **Orchestration**: http://localhost:8001 (docs: /docs)
- **MCP Server**: http://localhost:8002
- **Database**: localhost:5432

## Stop Services
```bash
docker-compose down
```

## Remove Everything
```bash
docker-compose down -v
```

---

**That's it! You're ready to go! 🎊**

For detailed documentation, see [README.md](README.md)
