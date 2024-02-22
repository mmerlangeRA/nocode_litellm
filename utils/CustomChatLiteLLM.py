from typing import Any, List, Optional
import uuid
from uuid import UUID
from langchain_community.chat_models import ChatLiteLLM
from litellm.integrations.custom_logger import CustomLogger
import litellm
from litellm import completion, acompletion
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.base import AsyncCallbackHandler 
from langchain_core.outputs import ChatGenerationChunk, GenerationChunk, LLMResult
from server.services.chat_service import ChatService

from server.services.service import Service

class MyCustomHandler(AsyncCallbackHandler):
    service:Service
    async def on_llm_end(
        self,
        response: LLMResult,
        *,
        run_id: UUID,
        parent_run_id: Optional[UUID] = None,
        tags: Optional[List[str]] = None,
        **kwargs: Any,
    ) -> None:
        if self.service:
            prompt_tokens=int(response.llm_output.get("token_usage").prompt_tokens)
            completion_tokens=int(response.llm_output.get("token_usage").completion_tokens)
            model =response.llm_output.get("model")
            self.service.add_consumption(prompt_tokens,completion_tokens, model)
    
    def log_pre_api_call(self, model, messages, kwargs): 
        print(f"Pre-API Call")
    
    def log_post_api_call(self, kwargs, response_obj, start_time, end_time): 
        print(f"Post-API Call")
        print(f"Response: {response_obj}")
    
    def log_stream_event(self, kwargs, response_obj, start_time, end_time):
        print(f"On Stream")
        
    def log_success_event(self, kwargs, response_obj, start_time, end_time): 
        try:
            print(f"On Success ?")
            print(f"kwargs: {kwargs}")
            print(f"Response: {response_obj}")
        except Exception as e:
            print(e)

    def log_failure_event(self, kwargs, response_obj, start_time, end_time): 
        print(f"On Failure")
        print(f"Response: {response_obj}")
    
    #### ASYNC #### - for acompletion/aembeddings
    
    async def async_log_stream_event(self, kwargs, response_obj, start_time, end_time):
        print(f"On Async Streaming")
        print(f"Response: {response_obj}")

    async def async_log_success_event(self, kwargs, response_obj, start_time, end_time):
        print(f"On Async Success")
        print(f"Response: {response_obj}")

    async def async_log_failure_event(self, kwargs, response_obj, start_time, end_time):
        print(f"On Async Success")
        print(f"Response: {response_obj}")





""" class CustomChatLiteLLM(ChatLiteLLM):
    def __init__(self,*kwargs):
        super().__init__(*kwargs)
        self.callbacks = [customHandler] """

async def custom_acompletion(*kwargs):
    return acompletion(*kwargs)

class CustomChatLiteLLM(ChatLiteLLM):
    service: Service 
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        customHandler = MyCustomHandler()
        customHandler.service = self.service
        self.callbacks=[customHandler]

