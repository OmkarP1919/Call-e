from fastapi import FastAPI
from fastapi.responses import JSONResponse

from app.graph.workflow import graph
from app.schemas import CallRequest, CallResponse


app = FastAPI(
    title="Broker CALL-E Agent"
)


@app.get("/")
def home():

    return {
        "message":
            "Broker CALL-E Agent is running"
    }


@app.post("/call", response_model=CallResponse)
def make_call(
    request: CallRequest
):

    state = {

        "phone_number":
            request.phone_number,

        "call_objective":
            request.objective or
            """
            Understand the customer's
            property requirements.
            """
    }

    try:

        result = graph.invoke(state)

    except ValueError as exc:

        return JSONResponse(
            status_code=400,
            content={
                "call_id": None,
                "success": False,
                "error": str(exc)
            }
        )

    except Exception as exc:

        return JSONResponse(
            status_code=500,
            content={
                "call_id": None,
                "success": False,
                "error": f"Unexpected error: {exc}"
            }
        )

    return {

        "call_id":
            result.get(
                "call_id"
            ),

        "success":
            result.get(
                "call_succeeded",
                False
            ),

        "call_status":
            result.get(
                "call_status"
            ),

        "gathered_information":
            result.get(
                "gathered_information"
            ),

        "error":
            result.get(
                "call_error"
            )
    }
