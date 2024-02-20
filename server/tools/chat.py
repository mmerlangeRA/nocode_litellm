
from server.utils.common_interfaces import OpenAIMessage,ChatBody
from litellm import completion, ModelResponse, CustomStreamWrapper,acompletion


async def chat(body:ChatBody):
    response = await acompletion(model=body.model, messages=body.messages, stream=body.stream)
    print("acompletion=")
    print(response)
    return response
