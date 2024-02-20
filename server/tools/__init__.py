from typing import List
from langchain_community.chat_models import ChatLiteLLM
from litellm.integrations.custom_logger import CustomLogger
import litellm
from litellm import completion, acompletion
from server.utils.common_interfaces import OpenAIMessage

class MyCustomHandler(CustomLogger):
    def log_pre_api_call(self, model, messages, kwargs): 
        print(f"Pre-API Call")
    
    def log_post_api_call(self, kwargs, response_obj, start_time, end_time): 
        print(f"Post-API Call")
        print(f"Response: {response_obj}")
    
    def log_stream_event(self, kwargs, response_obj, start_time, end_time):
        print(f"On Stream")
        
    def log_success_event(self, kwargs, response_obj, start_time, end_time): 
        print(f"On Success")
        print(f"Response: {response_obj}")

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

customHandler = MyCustomHandler()

litellm.callbacks = [customHandler]

""" class CustomChatLiteLLM(ChatLiteLLM):
    def __init__(self,*kwargs):
        super().__init__(*kwargs)
        self.callbacks = [customHandler] """

async def custom_acompletion(*kwargs):
    return acompletion(*kwargs)

#usage=Usage(completion_tokens=252, prompt_tokens=858