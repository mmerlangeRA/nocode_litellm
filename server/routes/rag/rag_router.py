import json
import logging
import os
from typing import Literal
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field
from components.rag.ingest import delete_chunks_by_file_id, delete_collection, ingest_document
from components.rag.query import get_all_chunks, get_chunk_by_id, query_documents
from server.utils.errors import INTERNAL_SERVER_ERROR_HTTPEXCEPTION
from server.utils.tokens import verify_token
logger = logging.getLogger(__name__)


class IngestRequest(BaseModel):
    file_url:str = Field(default="unknown")
    file_id:str = Field(default=None)
    file_name:str = Field(default="unknown")
    embeddingsProvider:str = Field(default="unknown")
    user_id:str = Field(default="unknown")
    class Config:
            schema_extra = {
                "examples": [{
                    "file_url": 'https://monpdf.fr',
                    "file_id": "supabase id",
                    "file_name": "test.pdf",
                    "embeddingsProvider": "openai",
                    "user_id":"741f03fc-22bc-45f6-b9ba-4a3064893b64"
                }]
            }

class FileItemsRequest(IngestRequest):
     user_id:str = Field(default=None)

class QueryRequest(BaseModel):
    query:str  = Field(description="the information to be looked for")
    source_count:int = Field(default=20)
    min_confidence: float = Field(default=0.2)
    file_ids:list = Field(default=[],description="the ids of the files to be queried")
    class Config:
            schema_extra = {
                "examples": [{
                    "query": 'What is the racket Djokovic uses ?',
                    "source_count":8,
                }]
            }


rag_router = APIRouter(prefix="/v1/rag")

@rag_router.post("/ingest", tags=["rag"])
async def ingest_route(request:Request,ingestRequest: IngestRequest, current_user: dict = Depends(verify_token)) :
     '''Use this api to get information from reference database'''
     try:
          print("ingest_route")
          print()
          await ingest_document(ingestRequest.file_url, ingestRequest.file_id, ingestRequest.file_name, ingestRequest.embeddingsProvider,ingestRequest.user_id)
          return {"response":"ingested"}
     except Exception as e:
          print(e)
          raise e

    

@rag_router.post("/query", tags=["rag"])
async def query_route(request:Request, queryRequest: QueryRequest, current_user: dict = Depends(verify_token)) :
    try:
         mostSimilarChunks = await query_documents(queryRequest.query,queryRequest.source_count,queryRequest.min_confidence, queryRequest.file_ids)
         return mostSimilarChunks
    except Exception as e:
         logger.error(e)
         raise INTERNAL_SERVER_ERROR_HTTPEXCEPTION(e)
    

@rag_router.get("/get_all_chunks", tags=["rag"])
async def get_chunk(request:Request) :
    try:
         chunks= get_all_chunks()
         return chunks
    except Exception as e:
         logger.error(e)
         raise INTERNAL_SERVER_ERROR_HTTPEXCEPTION(e)

@rag_router.get("/get_chunk/{chunk_id}", tags=["rag"])
async def get_chunk(chunk_id: str,request:Request) :
    print(chunk_id)
    try:
         chunk= get_chunk_by_id(chunk_id)
         print(chunk)
         return chunk
    except Exception as e:
         logger.error(e)
         raise INTERNAL_SERVER_ERROR_HTTPEXCEPTION(e)


@rag_router.post("/delete_collection", tags=["rag"])
async def delete_route(request:Request, collection_name: str, current_user: dict = Depends(verify_token)) :
    try:
         return delete_collection(collection_name)
    except Exception as e:
         logger.error(e)
         raise INTERNAL_SERVER_ERROR_HTTPEXCEPTION(e)

@rag_router.post("/delete_chunks_by_file_id/{file_id}", tags=["rag"])
async def delete_chunk(file_id: str, request:Request, current_user: dict = Depends(verify_token)) :
    try:
         print("delete_chunks_by_file_id ",file_id)
         return delete_chunks_by_file_id(file_id)
    except Exception as e:
         logger.error(e)
         raise INTERNAL_SERVER_ERROR_HTTPEXCEPTION(e)
