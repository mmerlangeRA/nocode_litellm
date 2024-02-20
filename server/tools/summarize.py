import os
from pydantic import BaseModel, Field
from litellm import completion, ModelResponse, CustomStreamWrapper
from pyparsing import List
from server.tools.get_document_from_url import get_document_from_url
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
from langchain.docstore.document import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter


defaut_prompt_template = """Write a concise summary of the following:
{text}
CONCISE SUMMARY:"""

default_refine_template=  (
        "Your job is to produce a final summary in  {lang}\n"
        "We have provided an existing summary up to a certain point: {existing_answer}\n"
        "We have the opportunity to refine the existing summary"
        "(only if needed) with some more context below.\n"
        "------------\n"
        "{text}\n"
        "------------\n"
        "If the context isn't useful, return the original summary."
    )

default_combine_prompt = """
    Write a concise summary of the following text delimited by triple backquotes.
    Return your response in bullet points which covers the key points of the text.
    ```{text}```
    BULLET POINT SUMMARY:
    """

class SummarizeRequest(BaseModel):
    prompt:str
    lang:str
    file_url:str
    model:str
    refine:bool = False
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "file_url":"https://www.fhi360.org/sites/default/files/media/documents/cfpb_building_block_activities_what-is-insurance_handout.pdf",
                    "lang": "fr",
                    "model":"gpt-3.5-turbo",
                    "refine":False,
                    "prompt": """Write a concise summary of the following:{text}CONCISE SUMMARY:""",
                }
            ]
        }}

async def summarize_map_text(text:str, model:str):

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=20,
        length_function=len,
        is_separator_regex=False,
    )
    docs  = text_splitter.create_documents([text])
    response =await summarize_refine(docs,model,"french")
    return response

    
async def summarize_map(lang:str, docs:List[Document], model="gpt-3.5-turbo"):

    llm = ChatLiteLLM(model=model,max_tokens="2000")
    # Map
    map_template = """The following is a set of documents
    {docs}
    Based on this list of docs, please identify the main themes 
    Helpful Answer:"""
    map_prompt = PromptTemplate.from_template(map_template)
    map_chain = LLMChain(llm=llm, prompt=map_prompt)

    reduce_template = "The following is set of summaries:\n{docs}\nTake these and distill it into a final, consolidated summary in "+lang+" of the main themes. Helpful Answer:"
    reduce_prompt = PromptTemplate.from_template(reduce_template)
    reduce_chain = LLMChain(llm=llm, prompt=reduce_prompt)

    # Takes a list of documents, combines them into a single string, and passes this to an LLMChain
    combine_documents_chain = StuffDocumentsChain(
        llm_chain=reduce_chain, document_variable_name="docs"
    )

    reduce_documents_chain = ReduceDocumentsChain(
        # This is final chain that is called.
        combine_documents_chain=combine_documents_chain,
        # If documents exceed context for `StuffDocumentsChain`
        collapse_documents_chain=combine_documents_chain,
        # The maximum number of tokens to group documents into.
        token_max=2000,
    )
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
    response=map_reduce_chain.run(split_docs)
    print(response)
    return response


async def summarize_refine(lang:str, split_docs:List[Document],model, refine_template = default_refine_template):
    llm = ChatLiteLLM(model=model)
    prompt_template = """Write a concise summary of the following:
    {text}
    CONCISE SUMMARY:"""
    prompt = PromptTemplate.from_template(prompt_template)

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

async def summarize(docs:List[Document],model, combine_prompt = default_combine_prompt):
    llm = ChatLiteLLM(model=model)
    map_prompt = """
    Write a concise summary of the following:
    "{text}"
    CONCISE SUMMARY:
    """
    map_prompt_template = PromptTemplate(template=map_prompt, input_variables=["text"])

    combine_prompt_template = PromptTemplate(template=combine_prompt, input_variables=["text"])
    summary_chain = load_summarize_chain(llm=llm,
                                     chain_type='map_reduce',
                                     map_prompt=map_prompt_template,
                                     combine_prompt=combine_prompt_template,
#                                      verbose=True
                                    )
    output = summary_chain.run(docs)
    print(output)
    return output
