import os
from typing import Literal
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field
from litellm import completion, ModelResponse, CustomStreamWrapper,acompletion
from server.utils.common_interfaces import OpenAIMessage,ChatBody
from server.utils.errors import FORBIDDEN_HTTPEXCEPTION
from server.utils.tokens import UserRights, generate_token, verify_token
from settings.settings import settings
from server.tools.chat import chat
import asyncio 




os.environ["OPENAI_API_KEY"] = settings().model_keys.openai
os.environ["MISTRAL_API_KEY"] = settings().model_keys.mistralai

completions_router = APIRouter(prefix="/v1")


@completions_router.post("/completion", tags=["completion"])
async def completion_route(request: Request, body: ChatBody, current_user: dict = Depends(verify_token)) :
    print(body)
    if body.model not in current_user['scope']['models']:
        raise FORBIDDEN_HTTPEXCEPTION(f"Invalid model requested {body.model} from {current_user['scope']['models']}")
    response = await chat(body)
    #response = await acompletion(model=body.model, messages=body.messages, stream=body.stream)
    return response
"""     if body.stream:
        return CustomStreamWrapper(response, model=body.model) """
    
