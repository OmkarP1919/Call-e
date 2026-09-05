from calle.errors import CalleAPIError, CalleConnectionError, CalleTimeoutError

from app.services.calle import make_broker_call, is_valid_e164
from app.services.storage import save_call


def validate_input(state):

    phone_number = state.get("phone_number", "").strip()

    if not phone_number:
        raise ValueError("Phone number is required.")

    if not is_valid_e164(phone_number):
        raise ValueError(
            f"Invalid phone number: {phone_number!r}. "
            "Must be in E.164 format, e.g. +919XXXXXXXXX."
        )

    return {"phone_number": phone_number}


def prepare_call(state):

    objective = state.get("call_objective")

    if not objective:

        objective = """
            Understand the customer's real-estate
            requirements for buying or renting a property.
        """

    return {
        "call_objective": objective
    }


def call_e_node(state):

    try:

        result = make_broker_call(
            phone_number=state["phone_number"],
            objective=state["call_objective"]
        )

    except ValueError as exc:

        return {
            "call_status": "error",
            "call_error": str(exc)
        }

    except CalleTimeoutError as exc:

        return {
            "call_status": "error",
            "call_error": str(exc)
        }

    except CalleConnectionError as exc:

        return {
            "call_status": "error",
            "call_error": str(exc)
        }

    except CalleAPIError as exc:

        return {
            "call_status": "error",
            "call_error": f"CALL-E API error ({exc.code}): {exc}"
        }

    except Exception as exc:

        return {
            "call_status": "error",
            "call_error": f"Unexpected error: {exc}"
        }

    return {
        "call_status": result.get("status"),
        "call_result": result
    }


def check_result(state):

    if state.get("call_error"):

        return {
            "call_succeeded": False
        }

    result = state.get("call_result") or {}

    status = result.get("status")
    task_completed = result.get("task_completed")
    structured_result = result.get("structured_result")

    succeeded = (
        status == "completed"
        and task_completed is True
        and isinstance(structured_result, dict)
    )

    return {
        "call_succeeded": succeeded,
        "gathered_information":
            structured_result if succeeded else None
    }


def store_result_node(state):

    save_call(
        phone_number=state["phone_number"],
        objective=state["call_objective"],
        result=state["call_result"],
        gathered_information=
            state["gathered_information"]
    )

    return {
        "stored": True
    }


def handle_failure_node(state):

    message = state.get("call_error")

    if not message:

        result = state.get("call_result") or {}

        message = (
            "Call did not succeed: "
            f"status={result.get('status')}, "
            f"task_completed={result.get('task_completed')}, "
            f"structured_result="
            f"{'present' if result.get('structured_result') else 'missing'}"
        )

    return {
        "stored": False,
        "call_error": message
    }
