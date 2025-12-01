# Test manually by calling the chatbot endpoint

import requests
import json

# Test chatbot endpoint
url = "http://localhost:8000/api/chat"

# You'll need a valid JWT token - get it from browser's localStorage or login first
# For now, let's just test if server is responding

try:
    # Test without auth to see if server is up
    response = requests.get("http://localhost:8000/docs")
    print(f"Server status: {response.status_code}")
    if response.status_code == 200:
        print("✅ Server is running")
    else:
        print(f"⚠️ Server returned: {response.status_code}")
except Exception as e:
    print(f"❌ Cannot connect to server: {e}")

print("\nTo test chatbot:")
print("1. Open browser DevTools (F12)")
print("2. Go to Application/Storage -> Local Storage")
print("3. Copy the 'token' value")
print("4. Use that token to make authenticated request")
