from pydantic import BaseModel, HttpUrl
from typing import Any, List, Optional, Dict, ForwardRef
from langchain_community.document_loaders import AsyncChromiumLoader
from langchain_community.document_transformers import BeautifulSoupTransformer

from langchain_community.document_transformers import Html2TextTransformer
from langchain_community.document_loaders import WebBaseLoader

from langchain.text_splitter import RecursiveCharacterTextSplitter
from bs4 import BeautifulSoup
from langchain.docstore.document import Document
from langchain_community.document_loaders import AsyncHtmlLoader

# import prompt template
from langchain import PromptTemplate
from bs4 import BeautifulSoup
import json
from abc import ABC, abstractmethod
from urllib.parse import urlparse
from pydantic import BaseModel

class Action(BaseModel):
    action: str
    tag: str
    attributes: Optional[Dict[str, Any]] = None
    extract: Optional[List[str]] = None
    children: Optional[List[Any]] = None

class QueryModel(BaseModel):
    url: HttpUrl
    query: List[Action]


""" class Action(BaseModel):
    action: str
    tag: str
    attributes: Optional[Dict[str, str]] = None
    extract: Optional[List[str]] = None
    children: Optional[List['Action']] = None

Action.update_forward_refs()

class QueryModel(BaseModel):
    url: HttpUrl
    query: List[Action] """

def get_base_url(url):
    parsed_url = urlparse(url)
    base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
    return base_url

class ScrapRequest(BaseModel):
    json_instructions: List[QueryModel]
    class Config:
            schema_extra = {
                "examples": [{
                    "json_instructions": [{
                        "url": "https://www.ecommercemag.fr/",
                        "query": [{
                            "action": "find_all",
                            "tag": "article",
                            "children": [{
                                "action": "find_all",
                                "tag": "h3",
                                "attributes": {"class": "derniers-jo"},
                                "children": [{
                                    "action": "find_all",
                                    "tag": "a",
                                    "extract": ["href"]
                                }]
                            }]
                        }]
                    }]
                }]
            }

class AbstractBSQueryHandler(ABC):
    @abstractmethod
    def query(self, html_content, query_instructions):
        pass

class BSQueryExecutor(AbstractBSQueryHandler):
   
    def query(self, base_parsing_url:str,html_content:str, query_instructions:List[Action], parent_soup=None):
        """ From a query will extract href or text, rendered in a list of {href/text: parsed}"""
        if parent_soup is None:
            soup = BeautifulSoup(html_content, 'html.parser')
        else:
            soup = parent_soup
        results = []
        base_url = get_base_url(base_parsing_url)
        for instruction_obj in query_instructions:
            if(isinstance(instruction_obj,Action)):
                instruction_obj = instruction_obj.dict()
            instruction= instruction_obj
            action = instruction.get('action')
            tag = instruction.get('tag')
            attributes = instruction.get('attributes', {})
            extracts = instruction.get('extract', [])
            children = instruction.get('children', [])

            if attributes is None:
                attributes = {}
            
            if action == 'find_all':
                found_elements = soup.find_all(tag, **attributes)
            elif action == 'find':
                found_elements = [soup.find(tag, **attributes)]
            else:
                raise ValueError(f"Unsupported action: {action}")

            for element in found_elements:
                if children is not None and len(children)>0:
                    child_results = self.query(base_parsing_url,"",children, parent_soup=element)
                    results  = results + child_results
                else:
                    result = {}
                    for extract in extracts:
                        if extract == 'href':
                            href = element.get('href')
                            if href and not href.startswith('http'):
                                href = f"{base_url.rstrip('/')}/{href.lstrip('/')}"
                            result['href'] = href
                        elif extract == 'text':
                            result['text'] = element.text.strip()
                        else:
                            result[extract] = element.get(extract)
                    results.append(result)

        return results
    
