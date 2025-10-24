from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from contextlib import asynccontextmanager
import uvicorn
import os
import logging
from typing import Dict, Any

# Import optimized components
from .config import config
from .security import init_security_manager, security_manager, require_security_validation
# from .monitoring import init_monitoring, get_system_metrics, performance_monitor
from .routers import chat, documents

# Configure logging
logging.basicConfig(
    level=getattr(logging, config.logging.level),
    format=config.logging.format,
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(os.path.join(config.logging.log_dir, 'app.log'), mode='a')
    ]
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting NEOC AI Assistant...")
    init_security_manager(config)
    # init_monitoring()  # Temporarily disabled
    yield
    # Shutdown
    logger.info("Shutting down NEOC AI Assistant...")

app = FastAPI(
    title="NEOC AI Assistant",
    description="Complete LLM application for disaster management with comprehensive hazard knowledge",
    version="2.0.0",
    lifespan=lifespan
)

# CORS middleware with configuration
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=config.api.cors_origins,
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# Security middleware for rate limiting
# @app.middleware("http")
# async def security_middleware(request: Request, call_next):
#     """Security middleware for request validation"""
#     # Get client identifier (IP-based for simplicity)
#     client_id = request.client.host if request.client else "unknown"

#     # Check rate limiting
#     if config.security.enable_rate_limiting and security_manager:
#         if not security_manager.rate_limiter.is_allowed(client_id):
#             return JSONResponse(
#                 status_code=429,
#                 content={"error": "Rate limit exceeded", "retry_after": 60}
#             )

#     response = await call_next(request)
#     return response

# Include routers with security
app.include_router(chat.router, prefix="/api/chat", tags=["chat"])
app.include_router(documents.router, prefix="/api/documents", tags=["documents"])

# Health check endpoint
@app.get("/health")
# @performance_monitor.monitor_function("health_check")
async def health_check():
    """Health check with comprehensive system status"""
    # from .monitoring import health_checker

    # health_status = health_checker.run_all_checks()
    # system_metrics = get_system_metrics()

    # Determine overall health
    # overall_healthy = (
    #     health_status.get('overall', {}).get('status') == 'healthy' and
    #     system_metrics['system']['memory_percent'] < 90
    # )

    return {
        "status": "healthy",
        "version": "2.0.0",
        # "system": system_metrics['system'],
        # "health_checks": health_status,
        # "config_valid": config.validate()
    }

# System metrics endpoint

# @app.get("/metrics")
# @performance_monitor.monitor_function("metrics_endpoint")
# async def get_metrics():
#     """Get comprehensive system and application metrics"""
#     return get_system_metrics()

# Mount static files
import os  # noqa: E402
static_dir = os.path.join(os.path.dirname(__file__), "../../static")
app.mount("/static", StaticFiles(directory=static_dir, html=True), name="static")

@app.get("/")
async def read_root():
    """Serve the main application"""
    return FileResponse(os.path.join(os.path.dirname(__file__), "../../static/index.html"))

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)