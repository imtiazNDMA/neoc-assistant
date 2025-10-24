#!/usr/bin/env python3
"""
Test script to start server and check health
"""

import subprocess
import time
import requests
import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

def test_server():
    print("Starting server...")
    # Start server in background
    server = subprocess.Popen([sys.executable, "main.py"], cwd=Path(__file__).parent)

    # Wait for startup
    time.sleep(10)

    try:
        # Check health
        response = requests.get("http://127.0.0.1:8000/health", timeout=5)
        print(f"Health check status: {response.status_code}")
        print(f"Health response: {response.json()}")

        # Check root
        response2 = requests.get("http://127.0.0.1:8000/", timeout=5)
        print(f"Root status: {response2.status_code}")
        print(f"Root content length: {len(response2.text)}")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        server.terminate()
        server.wait()

if __name__ == "__main__":
    test_server()