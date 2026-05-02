from pydantic_settings import BaseSettings
from functools import lru_cache
import os


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    # Server Configuration
    backend_host: str = os.getenv("BACKEND_HOST", "0.0.0.0")
    backend_port: int = int(os.getenv("BACKEND_PORT", 8000))
    environment: str = os.getenv("ENVIRONMENT", "development")
    debug: bool = environment == "development"
    
    # Database
    database_url: str = os.getenv("DATABASE_URL", "postgresql://chatbot_user:chatbot_password@localhost/chatbot_db")
    database_echo: bool = os.getenv("DATABASE_ECHO", "false").lower() == "true"
    
    # LLM Configuration
    ollama_host: str = os.getenv("OLLAMA_HOST", "http://localhost:11434")
    ollama_model: str = os.getenv("OLLAMA_MODEL", "qwen2.5:7b")
    llm_provider: str = os.getenv("LLM_PROVIDER", "ollama")
    temperature: float = float(os.getenv("TEMPERATURE", 0.7))
    max_tokens: int = int(os.getenv("MAX_TOKENS", 2048))
    
    # Embeddings
    embedding_model: str = os.getenv("OLLAMA_EMBEDDING_MODEL", "bge-small-en-v1.5")
    
    # Orchestration Service
    orchestration_url: str = os.getenv("ORCHESTRATION_URL", "http://localhost:8001")
    
    # MCP Server
    mcp_server_host: str = os.getenv("MCP_SERVER_HOST", "localhost")
    mcp_server_port: int = int(os.getenv("MCP_SERVER_PORT", 8002))
    
    # Speech Configuration
    speech_provider: str = os.getenv("SPEECH_PROVIDER", "openai")
    
    # Security
    secret_key: str = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
    cors_origins: list = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:3001").split(",")
    
    # Logging
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    log_format: str = os.getenv("LOG_FORMAT", "json")
    
    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
