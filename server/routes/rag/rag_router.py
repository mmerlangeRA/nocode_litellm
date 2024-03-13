import json
import logging
import os
from typing import Literal
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field
from components.rag.ingest import ingest_document, ingest_document_return_chunks
from components.rag.query import query_documents
from server.utils.errors import INTERNAL_SERVER_ERROR_HTTPEXCEPTION
from server.utils.tokens import verify_token
logger = logging.getLogger(__name__)


class IngestRequest(BaseModel):
    url:str = Field(default=None)
    file_id:str = Field(default=None)
    embeddingsProvider:str = Field(default=None)
    user_id:str = Field(default=None)
    class Config:
            schema_extra = {
                "examples": [{
                    "url": 'https://monpdf.fr',
                    "file_id": "supabase id",
                    "embeddingsProvider": "openai",
                    "user_id":"741f03fc-22bc-45f6-b9ba-4a3064893b64"
                }]
            }

class FileItemsRequest(IngestRequest):
     user_id:str = Field(default=None)

class QueryRequest(BaseModel):
    query:str
    class Config:
            schema_extra = {
                "examples": [{
                    "query": 'What is the racket Djokovic uses ?'
                }]
            }


rag_router = APIRouter(prefix="/v1/rag")

@rag_router.post("/ingest", tags=["rag"])
async def ingest_route(request:Request,queryRequest: IngestRequest, current_user: dict = Depends(verify_token)) :
    try:
         await ingest_document(queryRequest.url, queryRequest.file_id, queryRequest.embeddingsProvider)
         return {"response":"ingested"}
    except Exception as e:
         logger.error(e)
         raise INTERNAL_SERVER_ERROR_HTTPEXCEPTION(e)
    
@rag_router.post("/file_items_from_file", tags=["rag"])
async def ingest_route(request:Request, queryRequest: FileItemsRequest, current_user: dict = Depends(verify_token)) :
    try:
         file_items  = await ingest_document_return_chunks(queryRequest.url, queryRequest.file_id, queryRequest.embeddingsProvider, queryRequest.user_id)
         return {"file_items": file_items}
    except Exception as e:
         logger.error(e)
         raise INTERNAL_SERVER_ERROR_HTTPEXCEPTION(e)

@rag_router.post("/query", tags=["rag"])
async def query_route(request:Request, queryRequest: QueryRequest, current_user: dict = Depends(verify_token)) :
    try:
         mostSimilarChunks = await query_documents(queryRequest.query)
         return {"results":mostSimilarChunks}
    except Exception as e:
         logger.error(e)
         raise INTERNAL_SERVER_ERROR_HTTPEXCEPTION(e)
    

    