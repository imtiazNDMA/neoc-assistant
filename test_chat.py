import requests

# Test the chat API
url = "http://127.0.0.1:8000/api/chat/"
data = {"message": "Hello"}

print("Testing chat API...")
try:
    response = requests.post(url, json=data, timeout=60)  # Increased timeout
    print(f"Status: {response.status_code}")
    print(f"Response text: {response.text}")
    print(f"Response headers: {response.headers}")
    if response.status_code == 200:
        print(f"Response: {response.json()}")
except requests.exceptions.Timeout:
    print("Request timed out")
except requests.exceptions.RequestException as e:
    print(f"Request error: {e}")
except Exception as e:
    print(f"Error: {e}")