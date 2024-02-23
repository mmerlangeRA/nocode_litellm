import json
from typing import Annotated, Any, List, Tuple, Union
from langchain_community.document_loaders import WebBaseLoader
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.tools import tool
from langsmith import trace
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain_openai import ChatOpenAI
from pydantic import BaseModel
from nocode_litellm.tools.scraping.list_urls import list_all_article_urls_from_json_instructions
from tools.summarize import summarize_text
from server.services.chat_service import ChatService

from utils.CustomChatLiteLLM import CustomChatLiteLLM
from nocode_litellm.tools.scraping.scrapper import QueryModel,BSQueryExecutor
from langchain_core.output_parsers.json import parse_json_markdown



from tools.web_search import get_html_from_url
from langchain_community.document_loaders import AsyncHtmlLoader

json_parse=[
    {
"url":"https://www.ecommercemag.fr/",
  "query": [
    {
      "action": "find_all",
      "tag": "article",
      "children": [
        {
          "action": "find_all",
          "tag": "h3",
          "children": [
        {
          "action": "find_all",
          "tag": "a",
          "extract": ["href"]
        }
      ]
        }
      ]
    }
  ]
}
]

user_id="12345678-1234-5678-1234-567812345678"
service=ChatService(user_id=user_id)
llm = CustomChatLiteLLM(model="gpt-3.5-turbo",service=service, description="wzza")


@tool
async def get_best_article_summaries(json_instructions:List[QueryModel], instructions_for_ranking:str,nb_top_articles:int)->List[Any]:
    """This functions generates a list of summarized and ranked articles  
    It takes as input :
    - a list of query models (for scrapping)
    - instructions_for_ranking: instructions for summarization and ranking
    - nb_top_articles: the number of top ranked articles to return
    """
    print(instructions_for_ranking)
    print(nb_top_articles)
    print(json_instructions)

    href_results= await list_all_article_urls_from_json_instructions(json_instructions)
    print(href_results)
    urls=[]
    for i, key in enumerate(href_results):
        hrefs = href_results[key]
        print(hrefs)
        for href in hrefs: 
            print(href)
            url = href["href"]
            print(url)
            urls.append(url)
    
    top_articles = await summarize_articles_from_urls(urls, instructions_for_ranking,nb_top_articles)
    return top_articles

def create_agent(
    llm: ChatOpenAI,
    tools: list,
    system_prompt: str,
) -> str:
    system_prompt += "\nWork autonomously according to your specialty, using the tools available to you."
    " Do not ask for clarification."
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                system_prompt,
            ),
            MessagesPlaceholder(variable_name="messages"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ]
    )
    agent = create_openai_functions_agent(llm, tools, prompt)
    executor = AgentExecutor(agent=agent, tools=tools)
    return executor




research_agent = create_agent(
    llm,
    [get_best_article_summaries],
    """
    You are a journalist specialized in economic intelligence and monitoring (and short content creation), tasked with keeping your management informed of the economic and technological changes in the Retail sector.
    You task is to generate a list of summarized and ranked articles.
    As input, you have a list of query models (within triple quotes below).

    Here are the instructions for summarization and ranking:
    In text: identify one or two original and relevant themes for your monitoring and summarize everything in no more than 10 lines.
    Use line breaks for each theme. 
    Rate its relevance and insightfulness. 
    - Rate relevance according to to the Retail sector on a scale of 1 to 5, where 1 indicates not relevant and 5 indicates highly relevant: consider factors such as the mention of retail trends, challenges, opportunities, and specific retail industries.
    - Rate its insightfulness regarding economic and technological changes in the Retail sector on a scale of 1 to 5, where 1 indicates no insightful information and 5 indicates highly insightful: consider the depth of analysis, the mention of emerging technologies, economic impacts, and forward-looking statements.
        
    returns only the top 2 best article summaries. 
    
    ```
    {
"url":"https://www.ecommercemag.fr/",
  "query": [
    {
      "action": "find_all",
      "tag": "article",
      "children": [
        {
          "action": "find_all",
          "tag": "h3",
          "children": [
        {
          "action": "find_all",
          "tag": "a",
          "extract": ["href"]
        }
      ]
        }
      ]
    }
  ]
}
]
```, 
    """
)