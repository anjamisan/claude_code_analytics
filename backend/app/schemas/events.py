from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class TelemetryEvent(BaseModel):
    event_id: str
    user_id: str
    session_id: str
    event_name: str
    timestamp: datetime
    model: str
    input_tokens: int
    output_tokens: int
    duration_ms: int
    cost_usd: Optional[float] = None
    cache_read_tokens: Optional[int] = None
    cache_creation_tokens: Optional[int] = None

class ToolDecisionEvent(BaseModel):
    event_id: str
    user_id: str
    session_id: str
    event_name: str
    timestamp: datetime
    tool_name: str
    decision: str
    source: str

class ToolResultEvent(BaseModel):
    event_id: str
    user_id: str
    session_id: str
    event_name: str
    timestamp: datetime
    tool_name: str
    success: bool
    duration_ms: int
    decision_source: str
    decision_type: str
    tool_result_size_bytes: Optional[int] = None

class ApiErrorEvent(BaseModel):
    event_id: str
    user_id: str
    session_id: str
    event_name: str
    timestamp: datetime
    error: str
    status_code: str
    attempt: int
    duration_ms: int
    model: str