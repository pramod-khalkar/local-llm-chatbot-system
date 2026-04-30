from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from app.config.settings import get_settings
from app.utils.logger import logger
from app.models.database import engine, Base
from app.api import chat, speech, rag

settings = get_settings()


# Create tables on startup
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for app startup and shutdown."""
    # Startup
    logger.info("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    logger.info("✓ Application started successfully")
    
    yield
    
    # Shutdown
    logger.info("Application shutting down...")


# Create FastAPI app
app = FastAPI(
    title="LLM Chatbot Backend",
    description="Backend API for LLM-powered chatbot with RAG and MCP integration",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(chat.router)
app.include_router(speech.router)
app.include_router(rag.router)


@app.get("/api/config")
async def get_config():
    """Returns the current application configuration."""
    return {
        "model_name": settings.ollama_model,
        "environment": settings.environment,
        "version": "1.0.0"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "environment": settings.environment
    }


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "LLM Chatbot Backend API",
        "docs": "/docs",
        "health": "/health"
    }


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Custom HTTP exception handler."""
    logger.error(f"HTTP error {exc.status_code}: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code
        }
    )
