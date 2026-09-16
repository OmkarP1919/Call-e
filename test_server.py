import subprocess
import time
import requests
import json
import sys
import os
from pathlib import Path
from dotenv import load_dotenv

PROJECT_DIR = Path(__file__).resolve().parent
load_dotenv(PROJECT_DIR / ".env")

# Fallback test key if none exists
if not os.environ.get("CALLE_API_KEY"):
    os.environ["CALLE_API_KEY"] = "test-key"

test_phone = os.environ.get("CALLE_TEST_PHONE", "+919876543210")

# Start uvicorn server
server = subprocess.Popen([
    sys.executable, "-m", "uvicorn", "app.main:app", 
    "--host", "127.0.0.1", "--port", "8000"
], cwd=str(PROJECT_DIR))

try:
    # Wait for server to start
    time.sleep(3)
    
    # Test the API
    response = requests.post(
        "http://127.0.0.1:8000/call",
        json={
            "phone_number": test_phone,
            "objective": "Understand property requirements"
        }
    )
    
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
finally:
    # Stop server
    server.terminate()
    server.wait()