import json
import os
from typing import Literal
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field
from litellm import completion, ModelResponse, CustomStreamWrapper
from server.tools.scrapper import BSQueryExecutor, ScrapRequest, scrap_urls_to_Documents
from server.tools.get_document_from_url import get_document_from_url
from server.tools.summarize import SummarizeRequest, summarize_map, summarize_refine
from server.utils.errors import FORBIDDEN_HTTPEXCEPTION
from server.utils.tokens import UserRights, generate_token, verify_token
from settings.settings import settings
from langchain_community.chat_models import ChatLiteLLM

from langchain.chains.summarize import load_summarize_chain
from langchain_community.document_loaders import WebBaseLoader
from langchain.chains import MapReduceDocumentsChain, ReduceDocumentsChain
from langchain.text_splitter import CharacterTextSplitter
from langchain.prompts import PromptTemplate
from langchain.chains.llm import LLMChain
from langchain.chains.combine_documents.stuff import StuffDocumentsChain
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter


scrap_router = APIRouter(prefix="/v1")

@scrap_router.post("/scrap", tags=["scrap"])
async def load_route(request: ScrapRequest, url:str, current_user: dict = Depends(verify_token)) :
    json_instructions=request.body.json_instructions
    results={}
    if isinstance(json_instructions, str):
        list_instructions = json.loads(json_instructions)
    else:
        list_instructions = json_instructions
    
    for json_instruction in list_instructions:
        url = json_instruction["url"]
        docs = scrap_urls_to_Documents(url)
        executor = BSQueryExecutor()
        
        for doc in docs:
            html_content= doc.page_content
            results[url] = executor.query(url, html_content, json_instruction["query"])
    return {"response":results}