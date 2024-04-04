from pydantic import validator, Extra
from langchain.chat_models import AzureChatOpenAI


class AzureOpenAI(AzureChatOpenAI):
    deployment_name: str
    openai_api_key: str
    openai_api_version: str = "2023-07-01-preview"
    openai_api_type: str = "azure"
    openai_api_base: str = "<YOUR_API_BASE>"
    streaming: bool = False
    temperature: float = 0

    class Config:
        """Configuration for this pydantic object."""

        extra = Extra.allow
        arbitrary_types_allowed = True

    @validator("temperature")
    def validate_temperature(cls, request):
        if request < 0 or request > 1:
            raise ValueError("temperature must be between 0 and 1")

        return request