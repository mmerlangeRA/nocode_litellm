import os
from typing import Literal
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field
from litellm import completion, ModelResponse, CustomStreamWrapper
from server.utils.errors import FORBIDDEN_HTTPEXCEPTION
from server.utils.tokens import UserRights, generate_token, verify_token
from settings.settings import settings
from langchain_community.chat_models import ChatLiteLLM
chat = ChatLiteLLM(model="gpt-3.5-turbo")
from langchain.chains.summarize import load_summarize_chain
from langchain_community.document_loaders import WebBaseLoader
from langchain.chains import MapReduceDocumentsChain, ReduceDocumentsChain
from langchain.text_splitter import CharacterTextSplitter
from langchain.prompts import PromptTemplate
from langchain.chains.llm import LLMChain
from langchain.chains.combine_documents.stuff import StuffDocumentsChain
from langchain_community.document_loaders import PyPDFLoader



os.environ["OPENAI_API_KEY"] = settings().model_keys.openai

summarize_router = APIRouter(prefix="/v1")

class SummarizeRequest(BaseModel):
    prompt:str
    lang:str
    file:str
    model:str
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "prompt": "",
                    "lang": "fr",
                    "model":"gpt-3.5-turbo",
                    "file":"https://www.fhi360.org/sites/default/files/media/documents/cfpb_building_block_activities_what-is-insurance_handout.pdf"
                }
            ]
        }}

def summarize():
    loader = WebBaseLoader("https://lilianweng.github.io/posts/2023-06-23-agent/")
    docs = loader.load()

    llm = ChatLiteLLM(model="gpt-3.5-turbo",max_tokens="2000")
    chain = load_summarize_chain(llm, chain_type="stuff")
    return chain.run(docs)

async def summarize_map(basePrompt:str, lang:str, file:str, model):
    loader = PyPDFLoader(file)
    #loader = WebBaseLoader("https://nemato-data.fr/contactez-nous/")
    docs = loader.load()
    llm = ChatLiteLLM(model="gpt-3.5-turbo",max_tokens="2000")
    # Map
    map_template = """The following is a set of documents
    {docs}
    Based on this list of docs, please identify the main themes 
    Helpful Answer:"""
    map_prompt = PromptTemplate.from_template(map_template)
    map_chain = LLMChain(llm=llm, prompt=map_prompt)

    reduce_template = """The following is set of summaries:
    {docs}
    Take these and distill it into a final, consolidated summary of the main themes. 
    Helpful Answer:"""
    reduce_prompt = PromptTemplate.from_template(reduce_template)
    reduce_chain = LLMChain(llm=llm, prompt=reduce_prompt)

    # Takes a list of documents, combines them into a single string, and passes this to an LLMChain
    combine_documents_chain = StuffDocumentsChain(
        llm_chain=reduce_chain, document_variable_name="docs"
    )

    # Combines and iteratively reduces the mapped documents
    reduce_documents_chain = ReduceDocumentsChain(
        # This is final chain that is called.
        combine_documents_chain=combine_documents_chain,
        # If documents exceed context for `StuffDocumentsChain`
        collapse_documents_chain=combine_documents_chain,
        # The maximum number of tokens to group documents into.
        token_max=4000,
    )
    # Combining documents by mapping a chain over them, then combining results
    map_reduce_chain = MapReduceDocumentsChain(
        # Map chain
        llm_chain=map_chain,
        # Reduce chain
        reduce_documents_chain=reduce_documents_chain,
        # The variable name in the llm_chain to put the documents in
        document_variable_name="docs",
        # Return the results of the map steps in the output
        return_intermediate_steps=False,
    )

    text_splitter = CharacterTextSplitter.from_tiktoken_encoder(
        chunk_size=1000, chunk_overlap=0
    )
    split_docs = text_splitter.split_documents(docs)
    response =await summarize_refine(split_docs,model,lang)
    return response
    #return map_reduce_chain.run(split_docs)

async def summarize_refine(split_docs,model,lang):
    llm = ChatLiteLLM(model=model)
    prompt_template = """Write a concise summary of the following:
    {text}
    CONCISE SUMMARY:"""
    prompt = PromptTemplate.from_template(prompt_template)

    refine_template = (
        "Your job is to produce a final summary in "+lang+"\n"
        "We have provided an existing summary up to a certain point: {existing_answer}\n"
        "We have the opportunity to refine the existing summary"
        "(only if needed) with some more context below.\n"
        "------------\n"
        "{text}\n"
        "------------\n"
        "If the context isn't useful, return the original summary."
    )
    refine_prompt = PromptTemplate.from_template(refine_template)
    chain = load_summarize_chain(
        llm=llm,
        chain_type="refine",
        question_prompt=prompt,
        refine_prompt=refine_prompt,
        return_intermediate_steps=True,
        input_key="input_documents",
        output_key="output_text",
    )
    result = chain({"input_documents": split_docs}, return_only_outputs=True)
    return result["output_text"]


@summarize_router.post("/summarize", tags=["summarize"])
async def summarize_route(request: Request, body: SummarizeRequest, current_user: dict = Depends(verify_token)) :
    lang ="english"
    if body.lang =="fr":
        lang = "french"
    response = await summarize_map(body.prompt, lang, body.file,body.model)

    return {"response":response}