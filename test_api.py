#!/usr/bin/env python3
import requests
import json

# Test the chat API
url = "http://127.0.0.1:8000/api/chat/"
headers = {"Content-Type": "application/json"}
data = {"message": "Hello, test message", "conversation_id": "test123"}

try:
    response = requests.post(url, headers=headers, data=json.dumps(data))
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")