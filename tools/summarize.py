import json
from typing import Any
from langchain_openai import OpenAI
from pydantic import BaseModel, Field
from litellm import completion, ModelResponse, CustomStreamWrapper
from pyparsing import List
from server.services.summarize_service import SummarizeService
from tools.scraping.scrapper import BSQueryExecutor, get_base_url
from server.services.chat_service import ChatService
from utils.CustomChatLiteLLM import CustomChatLiteLLM
from server.tools.get_document_from_url import get_Documents_from_url
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
from langchain_core.tools import tool
from langchain_core.output_parsers.json import parse_json_markdown
from langchain_community.document_loaders import AsyncHtmlLoader
from langchain.document_loaders import PyPDFLoader


default_combine_prompt = """
    Write a concise summary in French of the following text delimited by triple backquotes.
    Return your response in bullet points which covers the key points of the text.
    ```{text}```
    BULLET POINT SUMMARY:
    """

'''
    service_id= uuid.UUID('{12345678-1234-5678-1234-567812345678}')
    print("service_id = "+str(service_id))
    llm = CustomChatLiteLLM(service_id=service_id,model=model)
    print("CustomChatLiteLLM initialized it seems")
'''


async def summarize_text(text:str, model:str = "gpt-3.5-turbo-instruct", combine_prompt:str = default_combine_prompt):
    """This function takes as text input, combine prompt and returns its summary"""
    try:
        print("model="+model)
        llm = OpenAI(model=model)
        docs = [Document(page_content=text)]
        
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
        output = await summary_chain.arun(docs)
        return output
    except Exception as e:
        print(e)
        raise FORBIDDEN_HTTPEXCEPTION("Error in summarize_text "+e )
    
async def summarize_Documents(docs:List[Document], model:str = "gpt-3.5-turbo-instruct", custom_prompt=default_combine_prompt):
    print("summarize_Documents")
    llm = OpenAI(model=model)
    combine_prompt_template = PromptTemplate(template=custom_prompt, input_variables=["text"])
    print("combine_prompt_template="+str(combine_prompt_template))
    summary_chain = load_summarize_chain(llm=llm,
                                    chain_type='map_reduce',
                                    combine_prompt=combine_prompt_template,
                                    )

    summary =  summary_chain.run(docs)

    return summary

async def summarize_articles_from_urls_returns_sorted_by_rank(urls:List[str],instructions_for_ranking:str,model="gpt-3.5-turbo-instruct")->List[Any]:
    scored_article_results=[]
    executor = BSQueryExecutor()

    queries={
        "https://www.ecommercemag.fr":[{
        "action":"find_all",
        "tag":"div",
        "attributes":{"class":"qiota_reserve"},
        "extract":["text"]
        }],
        "https://www.republik-retail.fr":[{
        "action":"find",
        "tag":"article",
        "extract":["text"]
        }],
        "https://www.journaldunet.com/retail":[{
        "action":"find",
        "tag":"div",
        "attributes":{"id":"jArticleInside"},
        "extract":["text"]
        }]
    }
        
    for url in urls:
        print("summarizing "+url)
        base_url = get_base_url(url)
        print("base_url="+base_url)
        query = queries.get(base_url)
        if query is None:
            print("no query for this base url")
            query=[{
        "action":"find_all",
        "tag":"p",
        "extract":["text"]
        }]

        docs = AsyncHtmlLoader(url).load()
        
        if(len(docs)==0):
            continue
        content = docs[0]
        #print(content)
        content = executor.query(url, content.page_content, query) 
        if(len(content)==0):
            continue
        html_text=""
        for c in content:
            html_text+=c["text"]+"\n"

        docs[0].page_content=html_text

        prompt_for_summarization = instructions_for_ranking + """```{text}```. 
        Important: return only a markdown formatted json with three properties: 'summary', 'relevance' and 'insightfulness'. 'relevance' and 'insightfulness' are integers ranking from 1 to 5.         
        """
        try:
            text = await summarize_text(text=html_text,combine_prompt= prompt_for_summarization, model=model)
            print(text)
            print("formatting")
            try:
                formatted=json.loads(text)    
            except:
                formatted = parse_json_markdown(text)

            
            print(formatted)
            relevance= int(formatted.get("relevance"))
            insightfulness= int(formatted.get("insightfulness"))
            result={
                "url":url,
                "text":formatted.get("summary"),
                "rank":relevance + insightfulness,
                "relevance":relevance,
                "insightfulness":insightfulness,
            }
            print(result)
            scored_article_results.append(result)
        except Exception as error:
            # handle the exception
            print("An exception occurred:", error)
            print("ERROR***********************")
    print(scored_article_results)
    return scored_article_results

'''        
async def summarize_pdf(pdf_file_path:str,  model:str = "gpt-3.5-turbo-instruct", custom_prompt=default_combine_prompt):
    try:    
        loader = PyPDFLoader(pdf_file_path)
        llm = OpenAI(model=model)
        docs = loader.load_and_split()
        combine_prompt_template = PromptTemplate(template=custom_prompt, input_variables=["text"])

        summary_chain = load_summarize_chain(llm=llm,
                                        chain_type='map_reduce',
                                        combine_prompt=combine_prompt_template,
    #                                      verbose=True
                                        )
        summary = await summary_chain.arun(docs)
        return summary
    except Exception as e:
        raise FORBIDDEN_HTTPEXCEPTION("Error in summarize_text")
'''