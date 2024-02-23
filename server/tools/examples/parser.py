# When availble, will need switch to llama_index ?
# source : https://docs.llamaindex.ai/en/stable/examples/output_parsing/openai_pydantic_program.html
from functools import partial
import json
import re
from langchain.chains.openai_functions import convert_to_openai_function
from langchain.utils.openai_functions import convert_pydantic_to_openai_function
import xml.etree.ElementTree as ET

from pydantic import BaseModel, Field, validator
from pydantic import BaseModel
from typing import List

from server.services.chat_service import ChatService

class BookRecommendation(BaseModel):
    """Provides book recommendations based on specified interest."""
    interest: str = Field(description="question of user interest about a book.")
    recommended_book: str = Field(description="answer to recommend a book")

    @validator("interest")
    def interests_must_not_be_empty(cls, info):
        if not info:
            raise ValueError("Interest cannot be empty.")
        return info

class Joke(BaseModel):
    """Get a joke that includes the setup and punchline"""
    setup: str = Field(description="question to set up a joke")
    punchline: str = Field(description="answer to resolve the joke")

    # You can add custom validation logic easily with Pydantic.
    @validator("setup")
    def question_ends_with_question_mark(cls, info):
        if info[-1] != "?":
            raise ValueError("Badly formed question!")
        return info

class SongRecommendation(BaseModel):
    """Provides song recommendations based on specified genre."""
    genre: str = Field(description="question to recommend a song.")
    song: str = Field(description="answer to recommend a song")

    @validator("genre")
    def genre_must_not_be_empty(cls, info):
        if not info:
            raise ValueError("genre cannot be empty.")
        return info



def extract_function_calls(completion):
    completion = completion.strip()
    pattern = r"(<multiplefunctions>(.*?)</multiplefunctions>)"
    match = re.search(pattern, completion, re.DOTALL)
    if not match:
        return None

    multiplefn = match.group(1)
    root = ET.fromstring(multiplefn)
    functions = root.findall("functioncall")
    return [json.loads(fn.text) for fn in functions]

def generate_hermes(service: ChatService, prompt:str):
    fn = """{"name": "function_name", "arguments": {"arg_1": "value_1", "arg_2": value_2, ...}}"""
    full_prompt = f"""<|im_start|>system
    You are a helpful assistant with access to the following functions:

    {convert_pydantic_to_openai_function(Joke)}

    {convert_pydantic_to_openai_function(BookRecommendation)}

    {convert_pydantic_to_openai_function(SongRecommendation)}

    To use these functions respond with:
    <multiplefunctions>
        <functioncall> {fn} </functioncall>
        <functioncall> {fn} </functioncall>
        ...
    </multiplefunctions>

    Edge cases you must handle:
    - If there are no functions that match the user request, you will respond politely that you cannot help.<|im_end|>
    <|im_start|>user
    {prompt}<|im_end|>
    <|im_start|>assistant"""
    messages = [
        ChatMessage(content=full_prompt, role=MessageRole("user"))
    ]
    response=service.chat(mode="openai", messages=messages)
    print("response")
    print(response.response)
    return response.response


