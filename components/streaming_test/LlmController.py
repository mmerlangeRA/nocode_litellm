import asyncio

from OpenAI import OpenAI
from typing import Union, List
from AzureOpenAI import AzureOpenAI
from pydantic import BaseModel, Extra
from langchain.schema.messages import BaseMessage
from langchain.chat_models.base import BaseChatModel
from langchain.base_language import BaseLanguageModel
from custom_callbacks import MyAsyncQueueCallbackHandler


class Llm(BaseModel):
    llm: BaseChatModel
    llm_name: str
    llm_args: dict
    callback: list = None

    class Config:
        """Configuration for this pydantic object."""

        extra = Extra.allow
        arbitrary_types_allowed = True

    def __str__(self):
        return f"llm: {self.llm_name} \n llm_args: {self.llm_args} \n"


class LangchainLlms:
    def __init__(self):
        self.__llms = {
            "OpenAI": {
                "llm": OpenAI,
                "schema": OpenAI

            },
            "AzureOpenAI": {
                "llm": AzureOpenAI,
                "schema": AzureOpenAI
            }

        }

    def get_llm(self, llm_name: str, callback=None, **llm_kwargs) -> Llm:
        if llm_name not in self.__llms:
            raise ValueError(f"invalid llm name given - {llm_name} , must be one of {list(self.__llms.keys())}")

        llm = self.__llms[llm_name]["llm"]
        llm_args = self.__llms[llm_name]["schema"](**llm_kwargs)
        llm_obj = llm(**dict(llm_args))

        return Llm(llm=llm_obj, llm_args=dict(llm_args), llm_name=llm_name, callback=callback)

    @staticmethod
    def try_setting_streaming_options(llm: Union[BaseChatModel, BaseLanguageModel]) -> Union[
        BaseChatModel, BaseLanguageModel]:
        # If the LLM type is OpenAI or ChatOpenAI, set streaming to True
        if isinstance(llm, BaseLanguageModel) or isinstance(llm, BaseChatModel):
            if hasattr(llm, "streaming") and isinstance(llm.streaming, bool):
                llm.streaming = True
                print("set streaming to true")
            elif hasattr(llm, "stream") and isinstance(llm.stream, bool):
                print("set streaming to true")
                llm.stream = True

        return llm

    @staticmethod
    async def get_non_stream_response(llm: BaseChatModel, messages: List[BaseMessage]) -> str:
        resp = await llm.apredict_messages(messages=messages)
        return resp.content

    @staticmethod
    async def get_stream_response(llm: BaseChatModel, messages: List[BaseMessage], cancel_token=None):
        llm = LangchainLlms.try_setting_streaming_options(llm)
        queue = asyncio.Queue()
        callback = AsyncQueueCallbackHandler(queue=queue, cancel_token=cancel_token)

        if hasattr(llm, "callbacks"):
            llm.callbacks = [callback]

        task = asyncio.create_task(llm.agenerate(messages=[messages]))
        token = ""

        while True:
            if cancel_token and cancel_token.is_cancelled is True:
                break

            try:
                token = await asyncio.wait_for(queue.get(), timeout=60 * 3)

                if token == "<END OF LLM RESPONSE>":
                    break

            except asyncio.TimeoutError:
                print("Consumer timed out waiting for a token.")
                task.cancel()
                raise asyncio.TimeoutError("Consumer timed out waiting for a token.")

            yield token