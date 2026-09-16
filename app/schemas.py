from pydantic import BaseModel
from typing import Optional


class CallRequest(BaseModel):
    phone_number: str
    objective: Optional[str] = None


class CallResponse(BaseModel):
    call_id: Optional[str] = None
    success: bool
    call_status: Optional[str] = None
    gathered_information: Optional[dict] = None
    error: Optional[str] = None
