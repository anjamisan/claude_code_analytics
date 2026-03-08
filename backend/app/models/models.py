# backend/models.py
from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional
from uuid import UUID

# ============================================
# EVENT Models
# ============================================

class EventBase(SQLModel): #so we don't have to repeat these fields in every model
    """Base event fields"""
    event_timestamp: datetime
    event_type: str  # api_request, tool_result, etc.
    user_id: Optional[str] = None
    user_email: str
    user_practice: Optional[str] = None
    session_id: Optional[UUID] = None
    organization_id: Optional[UUID] = None
    os_type: Optional[str] = None
    terminal_type: Optional[str] = None
    host_arch: Optional[str] = None


class Event(EventBase, table=True):
    """Database Event model"""
    __tablename__ = "events"
    
    event_id: Optional[int] = Field(default=None, primary_key=True)


class EventCreate(EventBase): #for post requests, we don't want to include event_id since it's auto-generated
    """Schema for creating event"""
    pass


class EventRead(EventBase): #for get requests, we want to include event_id
    """Schema for reading event"""
    event_id: int


# ============================================
# API REQUEST Models
# ============================================

class ApiRequestBase(SQLModel):
    """Base API request fields"""
    event_id: int
    model: str
    input_tokens: int
    output_tokens: int
    cost_usd: float
    duration_ms: int
    cache_read_tokens: int
    cache_creation_tokens: int


class ApiRequest(ApiRequestBase, table=True):
    """Database API Request model"""
    __tablename__ = "api_requests"
    
    request_id: Optional[int] = Field(default=None, primary_key=True)


class ApiRequestCreate(ApiRequestBase):
    """Schema for creating API request"""
    pass


class ApiRequestRead(ApiRequestBase):
    """Schema for reading API request"""
    request_id: int


# ============================================
# TOOL RESULT Models
# ============================================

class ToolResultBase(SQLModel):
    """Base tool result fields"""
    event_id: int
    tool_name: str
    success: bool
    duration_ms: int
    decision_type: str
    tool_result_size_bytes: Optional[int] = None


class ToolResult(ToolResultBase, table=True):
    """Database Tool Result model"""
    __tablename__ = "tool_results"
    
    result_id: Optional[int] = Field(default=None, primary_key=True)


class ToolResultCreate(ToolResultBase):
    """Schema for creating tool result"""
    pass


class ToolResultRead(ToolResultBase):
    """Schema for reading tool result"""
    result_id: int


# ============================================
# TOOL DECISION Models
# ============================================

class ToolDecisionBase(SQLModel):
    """Base tool decision fields"""
    event_id: int
    tool_name: str
    decision: str  # accept, reject
    source: str    # config, user_temporary, etc.


class ToolDecision(ToolDecisionBase, table=True):
    """Database Tool Decision model"""
    __tablename__ = "tool_decisions"
    
    decision_id: Optional[int] = Field(default=None, primary_key=True)


class ToolDecisionCreate(ToolDecisionBase):
    """Schema for creating tool decision"""
    pass


class ToolDecisionRead(ToolDecisionBase):
    """Schema for reading tool decision"""
    decision_id: int


# ============================================
# USER PROMPT Models
# ============================================

class UserPromptBase(SQLModel):
    """Base user prompt fields"""
    event_id: int
    prompt_length: int


class UserPrompt(UserPromptBase, table=True):
    """Database User Prompt model"""
    __tablename__ = "user_prompts"
    
    prompt_id: Optional[int] = Field(default=None, primary_key=True)


class UserPromptCreate(UserPromptBase):
    """Schema for creating user prompt"""
    pass


class UserPromptRead(UserPromptBase):
    """Schema for reading user prompt"""
    prompt_id: int


# ============================================
# API ERROR Models
# ============================================

class ApiErrorBase(SQLModel):
    """Base API error fields"""
    event_id: int
    error_message: str
    status_code: Optional[str] = None
    model: Optional[str] = None
    attempt: int
    duration_ms: int


class ApiError(ApiErrorBase, table=True):
    """Database API Error model"""
    __tablename__ = "api_errors"
    
    error_id: Optional[int] = Field(default=None, primary_key=True)


class ApiErrorCreate(ApiErrorBase):
    """Schema for creating API error"""
    pass


class ApiErrorRead(ApiErrorBase):
    """Schema for reading API error"""
    error_id: int


# ============================================
# EMPLOYEE Models
# ============================================

class EmployeeBase(SQLModel):
    """Base employee fields"""
    email: str
    full_name: str
    practice: str
    level: str
    location: str


class Employee(EmployeeBase, table=True):
    """Database Employee model"""
    __tablename__ = "employees"
    
    email: str = Field(primary_key=True)


class EmployeeCreate(EmployeeBase):
    """Schema for creating employee"""
    pass


class EmployeeRead(EmployeeBase):
    """Schema for reading employee"""
    pass


# ============================================
# ANALYTICS Response Models (View only)
# ============================================

class TokenUsageStats(SQLModel):
    """Token usage statistics"""
    practice: str
    total_input_tokens: int
    total_output_tokens: int
    avg_cost: float
    num_requests: int


class ToolStats(SQLModel):
    """Tool usage statistics"""
    tool_name: str
    usage_count: int
    success_rate: float
    avg_duration_ms: float


class PeakUsageTime(SQLModel):
    """Peak usage time statistics"""
    hour: int
    request_count: int
    total_tokens: int