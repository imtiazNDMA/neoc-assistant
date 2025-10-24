"""
Configuration management for NEOC AI Assistant
Following software engineering best practices for configuration
"""
import os
from typing import Dict, Any, Optional
from dataclasses import dataclass
from pathlib import Path

@dataclass
class DatabaseConfig:
    """Database configuration"""
    persist_dir: str = "chroma_db"
    cache_dir: str = ".cache"
    max_memory_mb: int = 500

@dataclass
class LLMConfig:
    """LLM configuration"""
    model_name: str = "phi3:latest"
    temperature: float = 0.1
    context_window: int = 2048
    cache_size: int = 50
    timeout: int = 30

@dataclass
class RAGConfig:
    """RAG pipeline configuration"""
    max_cache_size: int = 200
    chunk_size: int = 512
    chunk_overlap: int = 64
    max_search_results: int = 3
    similarity_threshold: float = 0.1

@dataclass
class APIConfig:
    """API configuration"""
    host: str = "0.0.0.0"
    port: int = 8000
    cors_origins: list = None
    max_request_size: int = 1000  # characters

    def __post_init__(self):
        if self.cors_origins is None:
            self.cors_origins = ["*"]

@dataclass
class LoggingConfig:
    """Logging configuration"""
    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    log_dir: str = "logs"
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    backup_count: int = 5

@dataclass
class SecurityConfig:
    """Security configuration"""
    enable_rate_limiting: bool = True
    max_requests_per_minute: int = 60
    enable_input_validation: bool = True
    max_input_length: int = 1000
    allowed_file_types: list = None

    def __post_init__(self):
        if self.allowed_file_types is None:
            self.allowed_file_types = ["pdf"]

class Config:
    """Main configuration class with environment variable support"""

    def __init__(self):
        # Load configuration from environment variables with defaults
        self.database = DatabaseConfig(
            persist_dir=os.getenv("DB_PERSIST_DIR", "chroma_db"),
            cache_dir=os.getenv("CACHE_DIR", ".cache"),
            max_memory_mb=int(os.getenv("MAX_MEMORY_MB", "500"))
        )

        self.llm = LLMConfig(
            model_name=os.getenv("LLM_MODEL", "phi3:latest"),
            temperature=float(os.getenv("LLM_TEMPERATURE", "0.1")),
            context_window=int(os.getenv("LLM_CONTEXT_WINDOW", "2048")),
            cache_size=int(os.getenv("LLM_CACHE_SIZE", "50")),
            timeout=int(os.getenv("LLM_TIMEOUT", "30"))
        )

        self.rag = RAGConfig(
            max_cache_size=int(os.getenv("RAG_CACHE_SIZE", "200")),
            chunk_size=int(os.getenv("CHUNK_SIZE", "512")),
            chunk_overlap=int(os.getenv("CHUNK_OVERLAP", "64")),
            max_search_results=int(os.getenv("MAX_SEARCH_RESULTS", "3")),
            similarity_threshold=float(os.getenv("SIMILARITY_THRESHOLD", "0.1"))
        )

        self.api = APIConfig(
            host=os.getenv("API_HOST", "0.0.0.0"),
            port=int(os.getenv("API_PORT", "8000")),
            max_request_size=int(os.getenv("MAX_REQUEST_SIZE", "1000"))
        )

        self.logging = LoggingConfig(
            level=os.getenv("LOG_LEVEL", "INFO"),
            log_dir=os.getenv("LOG_DIR", "logs")
        )

        self.security = SecurityConfig(
            enable_rate_limiting=os.getenv("ENABLE_RATE_LIMITING", "true").lower() == "true",
            max_requests_per_minute=int(os.getenv("MAX_REQUESTS_PER_MINUTE", "60")),
            max_input_length=int(os.getenv("MAX_INPUT_LENGTH", "1000"))
        )

        # Create necessary directories
        self._create_directories()

    def _create_directories(self) -> None:
        """Create necessary directories"""
        directories = [
            self.database.persist_dir,
            self.database.cache_dir,
            self.logging.log_dir,
            os.path.join(self.database.cache_dir, "embeddings")
        ]

        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)

    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary"""
        return {
            "database": {
                "persist_dir": self.database.persist_dir,
                "cache_dir": self.database.cache_dir,
                "max_memory_mb": self.database.max_memory_mb
            },
            "llm": {
                "model_name": self.llm.model_name,
                "temperature": self.llm.temperature,
                "context_window": self.llm.context_window,
                "cache_size": self.llm.cache_size,
                "timeout": self.llm.timeout
            },
            "rag": {
                "max_cache_size": self.rag.max_cache_size,
                "chunk_size": self.rag.chunk_size,
                "chunk_overlap": self.rag.chunk_overlap,
                "max_search_results": self.rag.max_search_results,
                "similarity_threshold": self.rag.similarity_threshold
            },
            "api": {
                "host": self.api.host,
                "port": self.api.port,
                "max_request_size": self.api.max_request_size
            },
            "logging": {
                "level": self.logging.level,
                "log_dir": self.logging.log_dir
            },
            "security": {
                "enable_rate_limiting": self.security.enable_rate_limiting,
                "max_requests_per_minute": self.security.max_requests_per_minute,
                "max_input_length": self.security.max_input_length
            }
        }

    def validate(self) -> bool:
        """Validate configuration values"""
        try:
            # Validate LLM config
            assert 0 <= self.llm.temperature <= 1, "Temperature must be between 0 and 1"
            assert self.llm.context_window > 0, "Context window must be positive"
            assert self.llm.cache_size > 0, "Cache size must be positive"

            # Validate RAG config
            assert self.rag.chunk_size > self.rag.chunk_overlap, "Chunk size must be greater than overlap"
            assert 0 <= self.rag.similarity_threshold <= 1, "Similarity threshold must be between 0 and 1"

            # Validate API config
            assert 1 <= self.api.port <= 65535, "Port must be between 1 and 65535"

            return True
        except AssertionError as e:
            print(f"Configuration validation failed: {e}")
            return False

# Global configuration instance
config = Config()

# Validate configuration on import
if not config.validate():
    raise ValueError("Invalid configuration. Please check your settings.")