from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class HCPCreate(BaseModel):
    name: str
    specialty: Optional[str] = None
    hospital: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None


class HCPOut(HCPCreate):
    id: str
    created_at: datetime

    class Config:
        from_attributes = True


class InteractionCreate(BaseModel):
    hcp_id: str
    interaction_type: Optional[str] = "visit"
    topics_discussed: Optional[str] = None
    samples_given: Optional[str] = None
    materials_shared: Optional[str] = None
    follow_up_required: Optional[bool] = False
    follow_up_notes: Optional[str] = None
    raw_input: Optional[str] = None  # if provided, LLM will parse/enrich this


class InteractionUpdate(BaseModel):
    interaction_type: Optional[str] = None
    topics_discussed: Optional[str] = None
    samples_given: Optional[str] = None
    materials_shared: Optional[str] = None
    follow_up_required: Optional[bool] = None
    follow_up_notes: Optional[str] = None
    summary: Optional[str] = None


class InteractionOut(BaseModel):
    id: str
    hcp_id: str
    interaction_type: Optional[str]
    interaction_date: datetime
    topics_discussed: Optional[str]
    samples_given: Optional[str]
    materials_shared: Optional[str]
    sentiment: Optional[str]
    summary: Optional[str]
    follow_up_required: Optional[bool]
    follow_up_notes: Optional[str]

    class Config:
        from_attributes = True


class ChatMessage(BaseModel):
    message: str
    hcp_id: Optional[str] = None          # if already known which HCP this is about
    interaction_id: Optional[str] = None  # set when the message is an edit to an existing log


class ChatResponse(BaseModel):
    reply: str
    tool_used: Optional[str] = None
    interaction_id: Optional[str] = None
    data: Optional[dict] = None
