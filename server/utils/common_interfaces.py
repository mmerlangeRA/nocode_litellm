from pydantic import BaseModel, Field
from typing import Any, Literal, List


class OpenAIMessage(BaseModel):
    """Inference result, with the source of the message.

    Role could be the assistant or system
    (providing a default response, not AI generated).
    """
    role: Literal["assistant", "system", "user"] = Field(default="user")
    content: str | None


class ChatBody(BaseModel):
    model: str
    messages: List[OpenAIMessage]
    include_sources: bool = True
    stream: bool = False
    tools: List[Any] = []

    class Config:
        schema_extra = {
            "examples": [
                {
                    "messages": [
                        {
                            "role": "system",
                            "content": "You are a rapper. Always answer with a rap.",
                        },
                        {
                            "role": "user",
                            "content": "How do you fry an egg?",
                        },
                    ],
                    "tools": [],
                    "include_sources": True,
                    "stream": False,
                    "model": "gpt-3.5-turbo"
                }
            ]
        }