import requests
import json

response = requests.post(
    "http://127.0.0.1:8000/call",
    json={
        "phone_number": "+919876543210",
        "objective": "Understand property requirements"
    }
)

print(f"Status: {response.status_code}")
print(f"Response: {json.dumps(response.json(), indent=2)}")