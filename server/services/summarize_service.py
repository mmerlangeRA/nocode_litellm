from server.tools import chat
from server.utils.common_interfaces import ChatBody
from server.services.service import Service,ServiceTpes
from litellm import completion, ModelResponse, CustomStreamWrapper,acompletion



class SummariezService(Service):
    def __init__(self, user_id:str):
        super().__init__(ServiceTpes.Summarize,user_id)

    async def process(self,body:ChatBody):
        response:ModelResponse =await chat(body) 
        if isinstance(response,ModelResponse):
            self.add_consumption(response.usage.get("prompt_tokens"), response.usage.get("completion_tokens"), response.model)
        


