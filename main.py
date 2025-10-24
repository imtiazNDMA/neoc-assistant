#!/usr/bin/env python3
"""
NEOC AI Assistant - Complete LLM application for disaster management
"""

import sys
import argparse
from pathlib import Path
import uvicorn

# Add src to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))
from neoc_assistant.app import app

def main(reload: bool = False, port: int = 8000):
    """Run the FastAPI server"""
    print("Starting NEOC AI Assistant server...")
    print("App routes:")
    for route in app.routes:
        print(f"  {route.path}")

    print(f"\nServer will be accessible at:")
    print(f"  - Web UI: http://localhost:{port}")
    print(f"  - API Docs: http://localhost:{port}/docs")
    print(f"  - Health Check: http://localhost:{port}/health")

    if reload:
        # For development with hot reload
        uvicorn.run("neoc_assistant.app:app", host="localhost", port=port, reload=True, log_level="warning")
    else:
        # For production without reload
        uvicorn.run(app, host="localhost", port=port, log_level="warning")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="NEOC AI Assistant Server")
    parser.add_argument("--reload", action="store_true", help="Enable hot reload for development")
    parser.add_argument("--no-reload", action="store_false", dest="reload", help="Disable hot reload (default)")
    parser.add_argument("--port", type=int, default=8000, help="Port to run the server on (default: 8000)")

    args = parser.parse_args()
    main(reload=args.reload, port=args.port)
