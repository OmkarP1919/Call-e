"""
Minimal CALL-E SDK test - official quickstart flow.

    phone number
        -> CALL-E
        -> call
        -> structured result

Requires CALLE_API_KEY and a test phone (E.164) in .env or the environment:

    CALLE_API_KEY=iams_live_...
    CALLE_TEST_PHONE=+919XXXXXXXXX

Run:
    python test_sdk_minimal.py
"""

import os
import uuid

from dotenv import load_dotenv
from calle import CalleClient

load_dotenv()

PHONE = (
    os.environ.get("CALLE_TEST_PHONE")
    or os.environ.get("CALLE_DEFAULT_PHONE")
    or ""
).strip()


def main():

    api_key = os.environ.get("CALLE_API_KEY")

    if not api_key:
        raise SystemExit(
            "CALLE_API_KEY is not set. Add it to .env or set it in the environment."
        )

    if not PHONE:
        raise SystemExit(
            "No test phone number set. Add CALLE_TEST_PHONE "
            "(E.164, e.g. +919XXXXXXXXX) to .env."
        )

    client = CalleClient(api_key=api_key)

    call = client.calls.create_and_wait(
        task=f"Call {PHONE} and ask whether they can hear clearly.",
        result_schema={
            "type": "object",
            "additionalProperties": False,
            "required": ["can_hear_clearly"],
            "properties": {
                "can_hear_clearly": {
                    "type": "string",
                    "enum": ["yes", "no", "unknown"],
                    "description": (
                        "The recipient's answer to the hearing check. "
                        "Use unknown if they did not answer or the evidence is ambiguous."
                    )
                }
            }
        },
        idempotency_key=f"hearing_check_{PHONE}_{uuid.uuid4().hex[:8]}",
        timeout_seconds=120,
        interval_seconds=2,
    )

    print(f"status: {call.get('status')}")
    print(f"task_completed: {call.get('task_completed')}")
    print(f"completion_confidence: {call.get('completion_confidence')}")
    print(f"evidence: {call.get('evidence')}")
    print(f"structured_result: {call.get('structured_result')}")

    if (
        call.get("status") != "completed"
        or call.get("task_completed") is not True
        or not isinstance(call.get("structured_result"), dict)
    ):
        raise SystemExit("CALL-E test call did not succeed.")


if __name__ == "__main__":
    main()
