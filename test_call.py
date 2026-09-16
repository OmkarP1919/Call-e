import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()

phone_number = (
    os.environ.get("CALLE_TEST_PHONE")
    or os.environ.get("CALLE_DEFAULT_PHONE")
    or "+919876543210"
).strip()

masked_phone = phone_number[:3] + "******" + phone_number[-2:] if len(phone_number) >= 5 else "***"
print(f"Sending test call request for {masked_phone} to local server...")

response = requests.post(
    "http://127.0.0.1:8000/call",
    json={
        "phone_number": phone_number,
        "objective": "Understand property requirements"
    }
)

print(f"Status: {response.status_code}")
print(f"Response: {json.dumps(response.json(), indent=2)}")