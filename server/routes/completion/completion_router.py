import os
from typing import Literal
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field
from litellm import completion, ModelResponse, CustomStreamWrapper,acompletion
from server.utils.errors import FORBIDDEN_HTTPEXCEPTION
from server.utils.tokens import UserRights, generate_token, verify_token
from settings.settings import settings
import asyncio 




os.environ["OPENAI_API_KEY"] = settings().model_keys.openai
os.environ["MISTRAL_API_KEY"] = settings().model_keys.mistralai

completions_router = APIRouter(prefix="/v1")


class OpenAIMessage(BaseModel):
    """Inference result, with the source of the message.

    Role could be the assistant or system
    (providing a default response, not AI generated).
    """
    role: Literal["assistant", "system", "user"] = Field(default="user")
    content: str | None


class ChatBody(BaseModel):
    model:str
    messages: list[OpenAIMessage]
    include_sources: bool = True
    stream: bool = False

    model_config = {
        "json_schema_extra": {
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
                    "stream": False,
                    "model":"gpt-3.5-turbo"
                }
            ]
        }
    }



@completions_router.post("/completion", tags=["completion"])
async def completion_route(request: Request, body: ChatBody, current_user: dict = Depends(verify_token)) :
    if body.model not in current_user['scope']['models']:
        raise FORBIDDEN_HTTPEXCEPTION("Invalid model requested "+body.model + " from "+current_user['scope']['models'])
    response = await acompletion(model=body.model, messages=body.messages, stream=body.stream)
    if body.stream:
        return CustomStreamWrapper(response)
    return response
