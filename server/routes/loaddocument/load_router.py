import os
from typing import Literal
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field
from litellm import completion, ModelResponse, CustomStreamWrapper
from nocode_litellm.server.tools.get_document_from_url import get_document_from_url
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



load_router = APIRouter(prefix="/v1")



@load_router.post("/load", tags=["summarize"])
async def load_route(request: Request, url:str, current_user: dict = Depends(verify_token)) :
    doc = await get_document_from_url(url)

    return {"response":doc}