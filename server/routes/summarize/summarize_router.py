import os
from typing import Literal
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field
from tools.summarize import summarize_text
from tools.scraping.scrapper import BSQueryExecutor
from server.utils.file_extension import get_file_extension
from server.tools import get_document_from_url
from server.utils.errors import FORBIDDEN_HTTPEXCEPTION, INTERNAL_SERVER_ERROR_HTTPEXCEPTION
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
from langchain.text_splitter import RecursiveCharacterTextSplitter

class SummarizeRequest(BaseModel):
    prompt:str
    file_url:str
    model:str
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "file_url":"https://www.fhi360.org/sites/default/files/media/documents/cfpb_building_block_activities_what-is-insurance_handout.pdf",
                    "model":"gpt-3.5-turbo",
                    "prompt": """Write a concise summary of the following:{text}CONCISE SUMMARY:""",
                }
            ]
        }}

summarize_router = APIRouter(prefix="/v1")

@summarize_router.post("/summarize_url", tags=["summarize"])
async def summarize_route(request: Request, body: SummarizeRequest, current_user: dict = Depends(verify_token)) :
    try:
        url = body.file_url
        docs = await get_document_from_url(url)

        executor = BSQueryExecutor()
        query={
            "action":"find",
            "tag":"div",
            "attributes":{"class":"qiota_reserve"},
            }
        content = docs[0]
        text = executor.query(url, content.page_content, query) 
        
        response = await summarize_text(text, model = body.model, combine_prompt=body.prompt)
        return {"response":response}
    except Exception as e:
        raise INTERNAL_SERVER_ERROR_HTTPEXCEPTION(str(e))


@summarize_router.post("/summarize_pdf_or_docx", tags=["summarize"])
async def summarize_route(request: Request, body: SummarizeRequest, current_user: dict = Depends(verify_token)) :
    try:
        url = body.file_url
        docs = await get_document_from_url(url)   
        text = docs[0].page_content 
        response = await summarize_text(text, model = body.model, combine_prompt=body.prompt)

        return {"response":response}
    except Exception as e:
        raise INTERNAL_SERVER_ERROR_HTTPEXCEPTION(str(e))


