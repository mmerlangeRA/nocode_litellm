import json
from typing import List
from tools.scraping.scrapper import BSQueryExecutor, QueryModel
from tools.web_search import get_html_from_url


async def list_all_article_urls_from_json_instructions(json_instructions:List[QueryModel]):
    """Returns structured list of article urls from a list of query models"""
    print("list_all_article_urls_from_json_instructions")
    href_results=[]
    print(json_instructions)
    if isinstance(json_instructions, str):
        list_instructions = json.loads(json_instructions)
    else:
        list_instructions = json_instructions
    print("parsed")
    for json_instruction in list_instructions:
        url = json_instruction.get("url")
        query = json_instruction.get("query")
        print("fteching "+url)
        html_content=  get_html_from_url(url)
        executor = BSQueryExecutor()
        list_articles = executor.query(url, html_content,query) 
        #remove duplicates
        seen = set()
        unique_array = [x for x in list_articles if x["href"] not in seen and not seen.add(x["href"])]

        href_results =href_results + unique_array
        #href_results[url]=list_articles[:5]
    return href_results