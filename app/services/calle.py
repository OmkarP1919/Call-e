import os
import re
from typing import Any, Dict, Optional

from dotenv import load_dotenv

from calle import CalleClient
from calle.errors import CalleAPIError, CalleConnectionError, CalleTimeoutError

load_dotenv()

API_KEY = os.environ.get("CALLE_API_KEY")
BASE_URL = os.environ.get("CALLE_BASE_URL", "https://api.heycall-e.com")

E164_RE = re.compile(r"^\+[1-9]\d{7,14}$")

_client: Optional[CalleClient] = None


def is_valid_e164(phone_number: str) -> bool:
    return bool(E164_RE.match(phone_number.strip()))


def get_client() -> CalleClient:
    global _client
    if _client is None:
        if not API_KEY:
            raise CalleAPIError(
                code="unauthorized",
                message="CALLE_API_KEY environment variable is missing. Add it to .env.",
                status_code=401,
            )
        _client = CalleClient(
            api_key=API_KEY,
            base_url=BASE_URL,
        )
    return _client


def make_broker_call(
    phone_number: str,
    objective: str,
    timeout_seconds: Optional[float] = None,
) -> Dict[str, Any]:
    """Place an outbound CALL-E call and wait for the structured result.

    The destination number goes directly in the task (no number purchase
    required). Never assume success: inspect the returned status /
    task_completed / structured_result before storing anything.
    """
    phone_number = phone_number.strip()

    if not is_valid_e164(phone_number):
        raise ValueError(
            f"Invalid phone number: {phone_number!r}. "
            "Must be in E.164 format, e.g. +919XXXXXXXXX."
        )

    client = get_client()

    workflow_run_id = f"broker_call_{phone_number}"

    call = client.calls.create_and_wait(
        task=_build_task(phone_number, objective),
        result_schema=_build_result_schema(),
        metadata={"workflow_run_id": workflow_run_id},
        idempotency_key=workflow_run_id,
        timeout_seconds=timeout_seconds or 300,
        interval_seconds=3,
    )

    return {
        "status": call.get("status"),
        "task_completed": call.get("task_completed"),
        "completion_confidence": call.get("completion_confidence"),
        "evidence": call.get("evidence"),
        "structured_result": call.get("structured_result"),
    }


def _build_task(phone_number: str, objective: str) -> str:
    return f"""
Call the customer at {phone_number}.

You are an AI assistant calling on behalf of a real-estate broker.

Your objective is to naturally understand the customer's property requirements.
{objective}

Ask about:
1. Whether they want to buy, sell, or rent.
2. Preferred location.
3. Property type.
4. Budget.
5. Number of bedrooms.
6. Preferred timeline.
7. Any additional requirements.

Have a natural conversation.
Do not ask all questions mechanically.
Adapt your questions based on the customer's answers.

At the end, politely thank the customer and end the call.

Return the collected information in the requested structured format.
"""


def _build_result_schema() -> Dict[str, Any]:
    return {
        "type": "object",
        "additionalProperties": False,
        "required": [
            "intent",
            "location",
            "property_type",
            "budget",
            "bedrooms",
            "timeline",
            "additional_requirements",
            "evidence_summary"
        ],
        "properties": {
            "intent": {
                "type": "string",
                "enum": ["buy", "sell", "rent", "unknown"],
                "description": (
                    "The customer's real-estate intent. Use buy if they want to "
                    "purchase a property, sell if they want to sell one, rent if "
                    "they want to rent. Use unknown if it was not stated clearly."
                )
            },
            "location": {
                "type": "string",
                "description": "Preferred location or area, or an empty string if not stated."
            },
            "property_type": {
                "type": "string",
                "description": "Type of property, e.g. 2BHK, 3BHK, apartment, villa, plot."
            },
            "budget": {
                "type": "string",
                "description": "Budget range as stated, e.g. 80 lakh or 25k per month."
            },
            "bedrooms": {
                "type": "string",
                "description": "Number of bedrooms required, e.g. 2."
            },
            "timeline": {
                "type": "string",
                "description": "Preferred timeline for buying, selling, or moving in."
            },
            "additional_requirements": {
                "type": "string",
                "description": "Any other requirements mentioned, e.g. parking, balcony, floor."
            },
            "evidence_summary": {
                "type": "string",
                "description": (
                    "One concise sentence citing the customer's words or behavior "
                    "that supports the collected details."
                )
            }
        }
    }
