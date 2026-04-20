# 🚀 LLM Chatbot - Launch Guide

## Status: ✅ READY TO LAUNCH

All components have been created and configured. The application is ready to start!

---

## 📋 Pre-Launch Checklist

- [x] Frontend (Next.js) - Created
- [x] Backend API (FastAPI) - Created
- [x] LLM Orchestration (FastAPI) - Created
- [x] MCP Server - Created
- [x] Docker Compose - Configured
- [x] All Dockerfiles - Created
- [x] Documentation - Complete
- [x] Environment Config - Ready

---

## 🚀 Launch Instructions

### Step 1: Ensure Docker is Running

**macOS:**
```bash
# Open Docker Desktop
open -a Docker

# Or if Docker is installed but not running
# Launch Docker.app from Applications folder
```

**Linux:**
```bash
# Start Docker daemon
sudo systemctl start docker

# Enable auto-start (optional)
sudo systemctl enable docker
```

**Windows:**
```bash
# Launch Docker Desktop from Start menu
```

### Step 2: Navigate to Project Directory

```bash
cd /Users/pramod/Documents/workspace/github/llm-chatbot
```

### Step 3: Start All Services

```bash
docker compose up -d
```

**Expected Output:**
```
[+] Running 6/6
 ✓ Container chatbot_postgres         Healthy
 ✓ Container chatbot_ollama           Started
 ✓ Container chatbot_backend          Started
 ✓ Container chatbot_llm_orchestration Started
 ✓ Container chatbot_mcp_server       Started
 ✓ Container chatbot_frontend         Started
```

### Step 4: Verify Services are Running

```bash
docker compose ps
```

**Expected Status:**
- `chatbot_postgres` - Healthy
- `chatbot_ollama` - Running
- `chatbot_backend` - Running
- `chatbot_llm_orchestration` - Running
- `chatbot_mcp_server` - Running
- `chatbot_frontend` - Running

### Step 5: Download LLM Models (Takes 2-4 minutes)

```bash
# Download Tinyllama model (lightweight, ~1-2 minutes) - DEFAULT
docker exec chatbot_ollama ollama pull tinyllama

# Alternative: Download Llama2 model (more powerful, ~2-3 minutes)
docker exec chatbot_ollama ollama pull llama2

# Download embeddings model (~1-2 minutes)
docker exec chatbot_ollama ollama pull nomic-embed-text
```

**Note:** The application defaults to `tinyllama` for faster inference. You can switch to `llama2` by setting `OLLAMA_MODEL=llama2` in `.env`.

### Step 6: Verify Services are Healthy

```bash
# Test backend API
curl http://localhost:8000/health

# Expected response:
# {"status":"healthy","version":"1.0.0","environment":"development"}
```

### Step 7: Open in Browser

```bash
# Open the application in your browser
open http://localhost:3000

# Or manually navigate to:
# http://localhost:3000
```

---

## 🔌 Service Endpoints

Once running, access services at:

| Service | URL | Purpose |
|---------|-----|---------|
| **Frontend UI** | http://localhost:3000 | Chat application |
| **Backend API** | http://localhost:8000 | REST API |
| **API Docs** | http://localhost:8000/docs | Swagger documentation |
| **Orchestration** | http://localhost:8001 | LLM orchestration |
| **Orchestration Docs** | http://localhost:8001/docs | Orchestration API docs |
| **MCP Server** | http://localhost:8002 | Tool/plugin management |
| **PostgreSQL** | localhost:5432 | Database (user: chatbot_user) |
| **Ollama** | http://localhost:11434 | LLM inference engine |

---

## 💬 Test the Application

Once running, try these interactions:

### Test 1: Basic Chat
1. Open http://localhost:3000
2. Type: "What is artificial intelligence?"
3. Click Send
4. Watch the bot respond!

### Test 2: Voice Input
1. Click the 🎤 microphone button
2. Speak clearly: "Hello, how are you?"
3. Click the microphone again to stop
4. Click Send
5. See the transcribed text and bot response

### Test 3: Tool Usage
1. Type: "Create a todo to buy groceries"
2. Watch the bot create the todo task

### Test 4: API Testing
1. Open http://localhost:8000/docs
2. Try the `/api/chat/sessions` endpoint
3. Create a chat session
4. Send a message

---

## 📊 Monitoring Services

### View Logs

```bash
# View all logs
docker compose logs

# View logs for specific service
docker compose logs backend
docker compose logs llm-orchestration
docker compose logs frontend

# Follow logs in real-time
docker compose logs -f
```

### Check Service Status

```bash
# Show running services
docker compose ps

# Show service resource usage
docker stats

# Inspect specific service
docker compose logs backend -f
```

---

## 🛑 Stopping Services

```bash
# Stop all services (keeps data)
docker compose down

# Stop and remove volumes (deletes data)
docker compose down -v

# Restart services
docker compose restart

# Restart specific service
docker compose restart backend
```

---

## 🔧 Troubleshooting

### Issue: "docker compose: command not found"

**Solution:** Use `docker-compose` instead (older Docker):
```bash
docker-compose up -d
docker-compose ps
```

Or ensure Docker is updated to version 20+.

### Issue: Services fail to start

**Solution:** Check Docker is running:
```bash
docker ps
```

If that fails, start Docker Desktop:
- macOS: `open -a Docker`
- Linux: `sudo systemctl start docker`

### Issue: Port already in use

**Solution:** Check what's using the port:
```bash
# macOS/Linux
lsof -i :3000
lsof -i :8000

# Kill the process
kill -9 <PID>
```

### Issue: Cannot connect to database

**Solution:** Wait a few seconds for PostgreSQL to initialize:
```bash
# Check database health
docker compose ps

# Wait for "Healthy" status
```

### Issue: Ollama models won't download

**Solution:** Verify Ollama container is running:
```bash
docker compose logs ollama

# Restart Ollama
docker compose restart ollama

# Try downloading again
docker exec chatbot_ollama ollama pull llama2
```

---

## 📈 Performance Tips

### For Faster Startup
```bash
# Build images in parallel
docker compose build --parallel

# Pre-pull base images
docker pull python:3.11-slim
docker pull node:18-alpine
docker pull postgres:15-alpine
docker pull ollama/ollama:latest
```

### For Better Performance
```bash
# Increase Docker memory allocation
# In Docker Desktop → Settings → Resources
# Set Memory: 8GB or higher

# Increase disk space if needed
# Monitor with: docker system df
```

---

## 🔐 Security Considerations

### For Development
- Default credentials are fine for local development
- See `.env` for current settings

### For Production
1. Change all default passwords in `.env`
2. Enable HTTPS/SSL
3. Configure CORS properly
4. Set strong SECRET_KEY
5. Use environment variables for secrets
6. Enable authentication
7. Set up backups for PostgreSQL
8. Configure log monitoring

---

## 📚 Documentation

For detailed information, see:

- **README.md** - Complete guide
- **QUICKSTART.md** - Quick start (5 minutes)
- **docs/ARCHITECTURE.md** - System design
- **docs/PROJECT_STRUCTURE.md** - File organization
- **SETUP_VERIFICATION.md** - Verification checklist

---

## ✨ Next Steps After Launch

1. **Explore the API**
   - Open http://localhost:8000/docs
   - Try different endpoints

2. **Test Features**
   - Text chat
   - Voice input
   - RAG search (index documents first)
   - Tool usage (create todos)

3. **Monitor Services**
   - Check logs: `docker compose logs -f`
   - Monitor resources: `docker stats`

4. **Customize (Optional)**
   - Edit `.env` for configuration
   - Modify `.env` for different LLM provider
   - Add custom tools to MCP server

5. **Deploy**
   - For cloud: See docs/ARCHITECTURE.md
   - For production: Follow security checklist

---

## 🎉 You're Ready!

The application is fully configured and ready to run. Just start Docker and execute:

```bash
cd /Users/pramod/Documents/workspace/github/llm-chatbot
docker compose up -d
```

Then open http://localhost:3000 in your browser! 🚀

---

**Happy chatting!** 🤖 💬

For support or issues, refer to the documentation or check logs with `docker compose logs -f`.
