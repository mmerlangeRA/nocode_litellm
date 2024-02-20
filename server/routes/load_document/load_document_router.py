import os
from typing import Literal
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field
from server.tools.get_document_from_url import get_document_from_url
from server.utils.errors import FORBIDDEN_HTTPEXCEPTION
from server.utils.tokens import UserRights, generate_token, verify_token
from settings.settings import settings


load_document_router = APIRouter(prefix="/v1")


@load_document_router.post("/load", tags=["load document"])
async def load_doc_route(request: Request, current_user: dict = Depends(verify_token)) :
    doc = await get_document_from_url(request.body.url)

    return {"response":doc}