#!/usr/bin/env python3
"""
Test script for NEOC AI Assistant Web UI
"""

import time

import requests


def test_ui():
    """Test if the web UI loads correctly"""
    try:
        print("Testing Web UI...")

        # Test root endpoint (should serve index.html)
        response = requests.get("http://localhost:8000/", timeout=5)
        if response.status_code == 200:
            content = response.text
            if "NEOC AI Assistant" in content and "<!DOCTYPE html>" in content:
                print("Web UI loads successfully")
                return True
            else:
                print("Web UI content is incorrect")
                return False
        else:
            print(f"Web UI returned status code: {response.status_code}")
            return False

    except requests.exceptions.RequestException as e:
        print(f"Could not connect to web UI: {e}")
        return False


def test_api():
    """Test if the API endpoints work"""
    try:
        print("Testing API endpoints...")

        # Test health endpoint
        response = requests.get("http://localhost:8000/api/health", timeout=5)
        if response.status_code == 200:
            print("Health endpoint works")
        else:
            print(f"Health endpoint returned: {response.status_code}")
            return False

        # Test chat endpoint
        chat_data = {
            "message": "Hello",
            "conversation_id": "test_" + str(int(time.time())),
        }
        response = requests.post(
            "http://localhost:8000/api/chat/", json=chat_data, timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            if "response" in data and "conversation_id" in data:
                print("Chat endpoint works")
                print(f"  Response preview: {data['response'][:100]}...")
                return True
            else:
                print("Chat endpoint returned incorrect data")
                return False
        else:
            print(f"Chat endpoint returned: {response.status_code}")
            return False

    except requests.exceptions.RequestException as e:
        print(f"Could not connect to API: {e}")
        return False


def main():
    """Run UI tests"""
    print("NEOC AI Assistant Web UI Test")
    print("=" * 30)

    # Note: This assumes the server is already running
    print("Note: Make sure the server is running with:")
    print("uv run uvicorn app:app --host 0.0.0.0 --port 8000 --reload")
    print()

    ui_test = test_ui()
    api_test = test_api()

    print()
    print("=" * 30)
    if ui_test and api_test:
        print("All tests passed! Web UI is working correctly.")
        print("Open http://localhost:8000 in your browser to use the chatbot.")
    else:
        print("Some tests failed. Check the server logs for errors.")


if __name__ == "__main__":
    main()
