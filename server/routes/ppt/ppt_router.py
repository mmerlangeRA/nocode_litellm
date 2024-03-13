import json
import logging
import os
from typing import List, Literal
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field
from components.rag.ingest import ingest_document, ingest_document_return_chunks
from components.rag.query import query_documents
from components.ppt.generator import create_presentation
from server.utils.errors import INTERNAL_SERVER_ERROR_HTTPEXCEPTION
from server.utils.tokens import verify_token
logger = logging.getLogger(__name__)


class PPTCreationRequest(BaseModel):
    topic:str=Field(default="",description="the topic of the presentation")
    slide_titles:List[str] = Field(default=[], description="the titles of the slides")
    slide_contents:List[str] = Field(default=[], description="the contents of the slides")
   
    class Config:
            schema_extra = {
                "examples": [{
                    "topic": 'Causes of diabet',
                    "slide_titles": ["title 1","title 2"],
                    "slide_contents": ["content 1","content 2"] 
                }]
            }


ppt_router = APIRouter(prefix="/v1/ppt") 


@ppt_router.post("/generate", tags=["ppt"])
async def ppt_generation_route(request:Request,queryRequest: PPTCreationRequest) :
    """Generate a slide presentation"""
    try:
         public_path = await create_presentation(queryRequest.topic, queryRequest.slide_titles, queryRequest.slide_contents)
         return {"url":public_path}
    except Exception as e:
         logger.error(e)
         raise INTERNAL_SERVER_ERROR_HTTPEXCEPTION(e)