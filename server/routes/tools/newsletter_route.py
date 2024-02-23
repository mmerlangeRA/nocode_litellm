import json
import os
from typing import List, Literal
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field
from litellm import completion, ModelResponse, CustomStreamWrapper
from server.database.client import create_file
from tools.scraping.list_urls import list_all_article_urls_from_json_instructions
from tools.summarize import summarize_articles_from_urls_returns_sorted_by_rank
from tools.scraping.scrapper import BSQueryExecutor, QueryModel
from server.utils.file_extension import get_file_extension
from server.tools import get_document_from_url
from server.utils.errors import FORBIDDEN_HTTPEXCEPTION, INTERNAL_SERVER_ERROR_HTTPEXCEPTION
from server.utils.tokens import UserRights, generate_token, verify_token

class NewsLetterRequest(BaseModel):
    instructions_for_finding:List[QueryModel]
    instructions_for_ranking:str
    model:str
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "instructions_for_finding":[
                        {
                            "url": "https://www.ecommercemag.fr/thematique/retail-1220",
                            "query": [
                                {
                                    "action": "find_all",
                                    "tag": "article",
                                    "children": [
                                        {
                                            "action": "find_all",
                                            "tag": "div",
                                            "attributes": {
                                                "class": "titre-bloc"
                                            },
                                            "children": [
                                                {
                                                    "action": "find_all",
                                                    "tag": "a",
                                                    "extract": [
                                                        "href"
                                                    ]
                                                }
                                            ]
                                        }
                                    ]
                                }
                            ]
                        },
                        {
                            "url": "https://www.republik-retail.fr/",
                            "query": [
                                {
                                    "action": "find_all",
                                    "tag": "a",
                                    "attributes": {
                                        "class": [
                                            "article__listing__itemsalune",
                                            "article__listing__item"
                                        ]
                                    },
                                    "extract": [
                                        "href"
                                    ]
                                }
                            ]
                        },
                        {
                            "url": "https://www.journaldunet.com/retail/",
                            "query": [
                                {
                                    "action": "find_all",
                                    "tag": "h2",
                                    "attributes": {
                                        "class": "app_title"
                                    },
                                    "children": [
                                        {
                                            "action": "find_all",
                                            "tag": "a",
                                            "extract": [
                                                "href"
                                            ]
                                        }
                                    ]
                                }
                            ]
                        }
                    ],
                    "model":"gpt-3.5-turbo-instruct",
                    "instructions_for_ranking": "Write a concise summary in French of the following text delimited by triple backquotes``{text}```Identify one or two original and relevant themes for your monitoring and summarize everything in no more than 100 words.Use line breaks between themes. Rate its relevance and insightfulness. Rate relevance according to to the Retail sector on a scale of 1 to 5, where 1 indicates not relevant and 5 indicates highly relevant: consider factors such as the mention of retail trends, challenges, opportunities, and specific retail industries. Rate its insightfulness regarding economic and technological changes in the Retail sector on a scale of 1 to 5, where 1 indicates no insightful information and 5 indicates highly insightful: consider the depth of analysis, the mention of emerging technologies, economic impacts, and forward-looking statements."
                }
            ]
        }}

class NewsLetterRequestString(BaseModel):
    instructions_for_ranking:str
    model:str
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "model":"gpt-3.5-turbo-instruct",
                    "instructions_for_ranking": "Write a concise summary in French of the following text delimited by triple backquotes``{text}```Identify one or two original and relevant themes for your monitoring and summarize everything in no more than 100 words.Use line breaks between themes. Rate its relevance and insightfulness. Rate relevance according to to the Retail sector on a scale of 1 to 5, where 1 indicates not relevant and 5 indicates highly relevant: consider factors such as the mention of retail trends, challenges, opportunities, and specific retail industries. Rate its insightfulness regarding economic and technological changes in the Retail sector on a scale of 1 to 5, where 1 indicates no insightful information and 5 indicates highly insightful: consider the depth of analysis, the mention of emerging technologies, economic impacts, and forward-looking statements."
                }
            ]
        }}


newsletter_router = APIRouter(prefix="/v1/tools")

@newsletter_router.post("/create_newsletter", tags=["newsletter"])
async def newsletter_route(request: Request, body: NewsLetterRequest) :
    try:
        print("newsletter_route")
        #scrap to get urls
        instructions_for_finding = body.instructions_for_finding
        instructions_for_ranking= body.instructions_for_ranking
        model = body.model
        print(instructions_for_finding)
        print(instructions_for_ranking)
        print("STARTING")
        list_hrefs = await list_all_article_urls_from_json_instructions(instructions_for_finding)
        urls = [href["href"] for href in list_hrefs]
        print(urls)
        #summarize and sort
        sorted_list = await summarize_articles_from_urls_returns_sorted_by_rank(urls,instructions_for_ranking,model=model)
        
        return {"response":sorted_list}
    except Exception as e:
        raise INTERNAL_SERVER_ERROR_HTTPEXCEPTION(str(e))
    
@newsletter_router.post("/create_newsletter_string", tags=["newsletter"])
async def newsletter_route(request: Request, body: NewsLetterRequestString) :
    try:
        print("newsletter_route")
        #scrap to get urls
        instructions_for_finding = [
                        {
                            "url": "https://www.ecommercemag.fr/thematique/retail-1220",
                            "query": [
                                {
                                    "action": "find_all",
                                    "tag": "article",
                                    "children": [
                                        {
                                            "action": "find_all",
                                            "tag": "div",
                                            "attributes": {
                                                "class": "titre-bloc"
                                            },
                                            "children": [
                                                {
                                                    "action": "find_all",
                                                    "tag": "a",
                                                    "extract": [
                                                        "href"
                                                    ]
                                                }
                                            ]
                                        }
                                    ]
                                }
                            ]
                        },
                        {
                            "url": "https://www.republik-retail.fr/",
                            "query": [
                                {
                                    "action": "find_all",
                                    "tag": "a",
                                    "attributes": {
                                        "class": [
                                            "article__listing__itemsalune",
                                            "article__listing__item"
                                        ]
                                    },
                                    "extract": [
                                        "href"
                                    ]
                                }
                            ]
                        },
                        {
                            "url": "https://www.journaldunet.com/retail/",
                            "query": [
                                {
                                    "action": "find_all",
                                    "tag": "h2",
                                    "attributes": {
                                        "class": "app_title"
                                    },
                                    "children": [
                                        {
                                            "action": "find_all",
                                            "tag": "a",
                                            "extract": [
                                                "href"
                                            ]
                                        }
                                    ]
                                }
                            ]
                        }
                    ]
        instructions_for_ranking= body.instructions_for_ranking
        model = body.model
        print(instructions_for_finding)
        print(instructions_for_ranking)
        print("STARTING")
        list_hrefs = await list_all_article_urls_from_json_instructions(instructions_for_finding)
        urls = [href["href"] for href in list_hrefs]
        print(urls)
        #summarize and sort
        sorted_list = await summarize_articles_from_urls_returns_sorted_by_rank(urls,instructions_for_ranking,model=model)
        return {"response":sorted_list}
    except Exception as e:
        raise INTERNAL_SERVER_ERROR_HTTPEXCEPTION(str(e))


@newsletter_router.get("/test", tags=["newsletter"])
async def newsletter_route(request: Request) :
    create_file()

@newsletter_router.get("/create_newsletter", tags=["newsletter"])
async def newsletter_route(request: Request) :
    try:
        print("newsletter_route get")
        #scrap to get urls
        instructions_for_finding = [
                        {
                            "url": "https://www.ecommercemag.fr/thematique/retail-1220",
                            "query": [
                                {
                                    "action": "find_all",
                                    "tag": "article",
                                    "children": [
                                        {
                                            "action": "find_all",
                                            "tag": "div",
                                            "attributes": {
                                                "class": "titre-bloc"
                                            },
                                            "children": [
                                                {
                                                    "action": "find_all",
                                                    "tag": "a",
                                                    "extract": [
                                                        "href"
                                                    ]
                                                }
                                            ]
                                        }
                                    ]
                                }
                            ]
                        }]
        instructions_for_ranking= "Write a concise summary in French of the following text delimited by triple backquotes``{text}```Identify one or two original and relevant themes for your monitoring and summarize everything in no more than 100 words.Use line breaks between themes. Rate its relevance and insightfulness. Rate relevance according to to the Retail sector on a scale of 1 to 5, where 1 indicates not relevant and 5 indicates highly relevant: consider factors such as the mention of retail trends, challenges, opportunities, and specific retail industries. Rate its insightfulness regarding economic and technological changes in the Retail sector on a scale of 1 to 5, where 1 indicates no insightful information and 5 indicates highly insightful: consider the depth of analysis, the mention of emerging technologies, economic impacts, and forward-looking statements."
        model = "gpt-3.5-turbo-instruct"
        print(instructions_for_finding)
        print(instructions_for_ranking)
        print("STARTING")
        list_hrefs = await list_all_article_urls_from_json_instructions(instructions_for_finding)
        urls = [href["href"] for href in list_hrefs]
        print(urls)
        #summarize and sort
        sorted_list = await summarize_articles_from_urls_returns_sorted_by_rank(urls,instructions_for_ranking,model=model)
        return {"response":sorted_list}
    except Exception as e:
        raise INTERNAL_SERVER_ERROR_HTTPEXCEPTION(str(e))