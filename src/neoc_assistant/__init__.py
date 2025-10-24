"""
NEOC AI Assistant - Complete LLM Application for Disaster Management
"""

__version__ = "2.0.0"
__author__ = "NEOC AI Assistant Team"

from .config import config
from .app import app
from .rag_pipeline import rag_pipeline
from .document_processor import document_processor
from .llm_service import llm_service

__all__ = [
    "config",
    "app",
    "rag_pipeline",
    "document_processor",
    "llm_service"
]