"""Schemas for the chat app."""
from pydantic import BaseModel, validator


class ChatResponse(BaseModel):
    """Chat response schema."""

    sender: str
    message: str
    type: str
    user_query: str = ""
    user_id: str = ""

    @validator("sender")
    def sender_must_be_bot_or_you(cls, v):
        if v not in ["bot", "you"]:
            raise ValueError("sender must be bot or you")
        return v

    @validator("type")
    def validate_message_type(cls, v):
        if v not in ["start", "stream", "end", "error", "info", "thought"]:
            raise ValueError("type must be start, stream or end")
        return v


class ChatRequest(BaseModel):
    """ Chat query schema"""
    query: str
    stop_generating: bool = False
