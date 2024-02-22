import os
from typing import Literal
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field
from litellm import completion, ModelResponse, CustomStreamWrapper
from tools.scrapper import BSQueryExecutor
from server.utils.file_extension import get_file_extension
from server.tools import get_document_from_url
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


chat = ChatLiteLLM(model="gpt-3.5-turbo")

os.environ["OPENAI_API_KEY"] = settings().model_keys.openai

summarize_router = APIRouter(prefix="/v1")



@summarize_router.post("/summarize", tags=["summarize"])
async def summarize_route(request: Request, body: SummarizeRequest, current_user: dict = Depends(verify_token)) :
    lang ="english"
    if body.lang =="fr":
        lang = "french"
    url = body.file_url
    docs = await get_document_from_url(url)
    file_extension=get_file_extension(url)
    
    if True and not file_extension == 'pdf':
        executor = BSQueryExecutor()
        query={
            "action":"find",
            "tag":"div",
            "attributes":{"class":"qiota_reserve"},
            }
        content = docs[0]
        content.page_content = executor.query(url, content.page_content, query) 
    
    response = await summarize_map(lang, docs,body.model,body.refine,body.prompt)

    return {"response":response}