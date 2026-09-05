import subprocess
import time
import requests
import json
import sys
import os

# Set environment variable
os.environ["CALLE_API_KEY"] = "test-key"

# Start uvicorn server
server = subprocess.Popen([
    sys.executable, "-m", "uvicorn", "app.main:app", 
    "--host", "127.0.0.1", "--port", "8000"
], cwd=r"E:\call-e\broker-call-agent")

try:
    # Wait for server to start
    time.sleep(3)
    
    # Test the API
    response = requests.post(
        "http://127.0.0.1:8000/call",
        json={
            "phone_number": "+919876543210",
            "objective": "Understand property requirements"
        }
    )
    
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
finally:
    # Stop server
    server.terminate()
    server.wait()