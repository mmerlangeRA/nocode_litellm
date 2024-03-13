from typing import List
#from langchain_community.tools.ddg_search.tool import DuckDuckGoSearchRun
#from langchain_community.utilities.wikipedia import WikipediaAPIWrapper
from langchain.docstore.document import Document
from langchain_community.document_loaders import AsyncHtmlLoader
from langchain_core.tools import tool
from langchain.agents import Tool

"""
wikipedia_tool = Tool(
    name="wikipedia",
    func=WikipediaAPIWrapper().run,
    description="Useful for when you need to look up the songwriters, genre, \
                and producers for a song on wikipedia",
) 

duckduckgo_tool = Tool(
    name="DuckDuckGo_Search",
    func=DuckDuckGoSearchRun().run,
    description="Useful for when you need to do a search on the internet to find \
                information that the other tools can't find.",
)
"""

def scrap_urls_to_Documents(urls:List[str])->List[Document]:
    loader = AsyncHtmlLoader(urls)
    docs = loader.load()
    return docs

@tool
def get_html_from_url(url:str)->str:
    """Returns html content from an url"""
    html = scrap_urls_to_Documents([url])[0].page_content
    return html