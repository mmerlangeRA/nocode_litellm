from pydantic import BaseModel, Field, ConfigDict
from typing import Any, Literal, List, Union


class OpenAIMessage(BaseModel):
    """
    Inference result, with the source of the message.

    Role could be the assistant, system
    (providing a default response, not AI generated), or user.
    """
    role: Literal["assistant", "system", "user"] = Field(default="user")
    content: Union[str, None]


class ChatBody(BaseModel):
    model: str
    messages: List[OpenAIMessage]
    include_sources: bool = Field(default=True)
    stream: bool = Field(default=False)
    tools: List[Any] = Field(default_factory=list)

    model_config = ConfigDict(
        json_schema_extra={
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
                    "model": "gpt-3.5-turbo",
                }
            ]
        }
    )
