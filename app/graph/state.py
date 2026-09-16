from typing import TypedDict, Optional, Dict, Any


class BrokerCallState(TypedDict, total=False):

    phone_number: str
    call_objective: str

    call_id: Optional[str]

    call_status: str

    call_result: Dict[str, Any]

    call_error: str
    call_succeeded: bool

    gathered_information: Dict[str, Any]

    stored: bool
