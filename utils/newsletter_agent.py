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
from tools.summarize import summarize_text
from server.services.chat_service import ChatService

from utils.CustomChatLiteLLM import CustomChatLiteLLM
from tools.scrapper import QueryModel,BSQueryExecutor
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


async def list_all_article_urls_from_json_instructions(json_instructions:List[QueryModel]):
    """Returns structured list of article urls from a list of query models"""
    href_results={}
    if isinstance(json_instructions, str):
        list_instructions = json.loads(json_instructions)
    else:
        list_instructions = json_instructions
    
    for json_instruction in list_instructions:
        url = json_instruction.url
        html_content=  get_html_from_url(url)
        executor = BSQueryExecutor()
        list_articles = executor.query(url, html_content, json_instruction.query) 
        href_results[url]=list_articles[:5]
    return href_results



async def summarize_articles_from_urls(urls:List[str],instructions_for_ranking:str,nb_articles:int)->List[Any]:
    scored_article_results=[]
    executor = BSQueryExecutor()
    query=[{
        "action":"find_all",
        "tag":"div",
        "attributes":{"class":"qiota_reserve"},
        "extract":["text"]
        }]
        
    for url in urls:
        print("summarizing "+url)
        docs = AsyncHtmlLoader(url).load()
        
        if(len(docs)==0):
            continue
        content = docs[0]
        #print(content)
        content = executor.query(url, content.page_content, query) 
        if(len(content)==0):
            continue
        html_text:str = content[0]["text"]
        docs[0].page_content=html_text

        prompt_for_summarization = instructions_for_ranking + """```{text}```. 
        Important, return only a formatted json with three propertiers: 'summary', 'relevance' and 'insightfulness'. 'relevance' and 'insightfulness' are just integers ranking from 1 to 5.         
        """
        try:
            text = await summarize_text(html_text,prompt_for_summarization)
            print(text)
            print("formatting")
            formatted = parse_json_markdown(text)
            print(formatted)
            result={
                "url":url,
                "text":formatted.get("summary"),
                "rank":int(formatted.get("relevance"))+int(formatted.get("insightfulness"))
            }
            print(result)
            scored_article_results.append(result)
        except Exception as error:
            # handle the exception
            print("An exception occurred:", error)
            print("ERROR***********************")
    print(scored_article_results)
    return scored_article_results
    sorted_array = sorted(scored_article_results, key=lambda x: x.rank, reverse=True)
    top_articles = sorted_array[:nb_articles]
    return top_articles
        

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