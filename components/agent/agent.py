from typing import Any, Dict, List, Optional
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Extra, HttpUrl
import requests
import urllib3
import urllib.parse

llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0,openai_api_key="")

from langchain.agents import tool

from langchain.tools import BaseTool, StructuredTool, tool


class Property(BaseModel):
    type: str
    description: str

class Info(BaseModel):
    title: str
    description: str
    server: HttpUrl

class Route(BaseModel):
    path: str
    method: str
    operationId: str
    requestInBody: bool

class Custom_Parameters(BaseModel):
    type:str
    properties:Property

class Custom_Function_Parms(BaseModel):
    name:str
    description:str
    parameters:Custom_Parameters

class Custom_Function(BaseModel):
    type: str
    function:Custom_Function_Parms


class APIModel(BaseModel):
    info: Info
    routes: List[Route]
    functions: List[Custom_Function]

class EventsAPIWrapper(StructuredTool):
    url:str
    def __init__(self, model: APIModel, **data):
        super().__init__(name=model.info.title,args_schema=model.functions[0].function.parameters.properties, url=model.info.server + model.routes[0].path) 
        self.url = model.info.server + model.routes[0].path
        #self.name = model.info.title
        self.description = model.info.description
        #self.args_schema = model.functions[0].function.parameters.properties

    def run(self, body) -> str:
        encoded_query =  "youpi"
        encoded_filter_by_country =  urllib.parse.quote_plus(self.filter_by_country)
        response = requests.get(f"https://events.brahmakumaris.org/events-rest/event-search-v2?search={encoded_query}" + 
                     f"&limit=10&offset={self.offset}&filterByCountry={encoded_filter_by_country}&includeDescription=true")
        if response.status_code >= 200 and response.status_code < 300:
            json = response.json()
            summaries = [self._formatted_event_summary(e) for e in json['events']]
            return "\n\n".join(summaries)[: self.doc_content_chars_max]
        else:
            return f"Failed to call events API with status code {response.status_code}"

    @staticmethod
    def _formatted_event_summary(event: Dict) -> Optional[str]:
        return (f"Event: {event['name']}\n" + 
                f"Start: {event['startDate']} {event['startTime']}\n" + 
                f"End: {event['endDate']} {event['endTime']}\n" +
                f"Venue: {event['venueAddress']} {event['postalCode']} {event['locality']} {event['countryName']}\n" +
                f"Event Description: {event['description']}\n" +
                f"Event URL: https://brahmakumaris.uk/event/?id={event['id']}\n"
        )

json = '{"info":{"title":"ppt","description":"Generate a pptx presentation from slide descriptions","server":"http://nocode.nemato-data.fr"},"routes":[{"path":"/v1/ppt/generate","method":"post","operationId":"ppt_generation_route_v1_ppt_generate_post","requestInBody":true}],"functions":[{"type":"function","function":{"name":"ppt_generation_route_v1_ppt_generate_post","description":"Generate a slide presentation","parameters":{"type":"object","properties":{"requestBody":{"type":"object","properties":{"topic":{"type":"string","title":"Topic","description":"the topic of the presentation","default":""},"slide_titles":{"items":{"type":"string"},"type":"array","title":"Slide Titles","description":"the titles of the slides","default":[]},"slide_contents":{"items":{"type":"string"},"type":"array","title":"Slide Contents","description":"the contents of the slides","default":[]}}}}}}}]}'
model:APIModel=APIModel.parse_raw(json)

events=EventsAPIWrapper(model)

""" StructuredTool.from_function(
            func=events.run,
            name="Events",
            description="useful when you need an answer about meditation related events in the united kingdom"
        ), """


def create_tool(model:APIModel) -> StructuredTool:
    url = model.info.server + model.routes[0].path

    return StructuredTool(
        name=model.info.title,
        description=model.info.description,
        func=lambda x: x,
        args_schema=model,
    )  


@tool
def get_word_length(word: str) -> int:
    """Returns the length of a word."""
    return len(word)


#get_word_length.invoke("abc")

tools = [get_word_length]
print(tools)

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are very powerful assistant, but don't know current events",
        ),
        ("user", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ]
)

llm_with_tools = llm.bind_tools(tools)

from langchain.agents.format_scratchpad.openai_tools import (
    format_to_openai_tool_messages,
)
from langchain.agents.output_parsers.openai_tools import OpenAIToolsAgentOutputParser

agent = (
    {
        "input": lambda x: x["input"],
        "agent_scratchpad": lambda x: format_to_openai_tool_messages(
            x["intermediate_steps"]
        ),
    }
    | prompt
    | llm_with_tools
    | OpenAIToolsAgentOutputParser()
)

from langchain.agents import AgentExecutor

agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

list(agent_executor.stream({"input": "How many letters in the word eudca"}))