"""
Broker CALL-E SDK test using the reusable make_broker_call service.

    phone number
        -> make_broker_call
        -> CALL-E
        -> outbound call
        -> structured requirements

Requires CALLE_API_KEY and a test phone (E.164) in .env or the environment:

    CALLE_API_KEY=iams_live_...
    CALLE_TEST_PHONE=+919XXXXXXXXX

Run:
    python test_sdk_broker.py
"""

import os
import sys

from dotenv import load_dotenv

load_dotenv()

from app.services.calle import make_broker_call

PHONE = (
    os.environ.get("CALLE_TEST_PHONE")
    or os.environ.get("CALLE_DEFAULT_PHONE")
    or ""
).strip()


def main():

    if not os.environ.get("CALLE_API_KEY"):
        raise SystemExit(
            "CALLE_API_KEY is not set. Add it to .env or set it in the environment."
        )

    if not PHONE:
        raise SystemExit(
            "No test phone number set. Add CALLE_TEST_PHONE "
            "(E.164, e.g. +919XXXXXXXXX) to .env."
        )

    result = make_broker_call(
        phone_number=PHONE,
        objective="Understand the customer's requirements for buying or renting a residential property.",
    )

    print(f"call_id: {result.get('call_id')}")
    print(f"status: {result.get('status')}")
    print(f"task_completed: {result.get('task_completed')}")
    print(f"completion_confidence: {result.get('completion_confidence')}")
    print(f"evidence: {result.get('evidence')}")
    print(f"structured_result: {result.get('structured_result')}")

    succeeded = (
        result.get("status") == "completed"
        and result.get("task_completed") is True
        and isinstance(result.get("structured_result"), dict)
    )

    if not succeeded:
        print("Broker call did not succeed - nothing was stored.")
        sys.exit(1)


if __name__ == "__main__":
    main()
