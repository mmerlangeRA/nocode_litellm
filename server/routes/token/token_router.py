import os
from typing import Literal
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field
from litellm import completion, ModelResponse, CustomStreamWrapper,acompletion
from server.utils.errors import FORBIDDEN_HTTPEXCEPTION
from server.utils.tokens import UserRights, generate_token, verify_token
from settings.settings import settings


token_router = APIRouter(prefix="/v1")

class GenerateTokenBody(BaseModel):
    admin_key: str
    user_rights: UserRights
    model_config= {
        "json_schema_extra": {
            "examples": [
                {
                    "admin_key":"xxx",
                    "user_rights": {
                        "models": ["gpt-3.5-turbo","mistral/mistral-tiny"]}
                    }
                ]
            }
        }



@token_router.post("/token", tags=["token"])
def get_token(request: Request, body: GenerateTokenBody):
    if body.admin_key != settings().token.admin_key:
        raise FORBIDDEN_HTTPEXCEPTION("Invalid admin key "+body.admin_key )
    return generate_token({
        "models":body.user_rights.models
        })


