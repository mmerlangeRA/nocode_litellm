from pydantic import validator, Extra
from langchain.chat_models import ChatOpenAI


class OpenAI(ChatOpenAI):
    model_name: str = "gpt-4"
    temperature: float = 0
    openai_api_key: str
    streaming: bool = True

    class Config:
        """Configuration for this pydantic object."""

        extra = Extra.allow
        arbitrary_types_allowed = True

    @validator("temperature")
    def validate_temperature(cls, request):
        if request < 0 or request > 1:
            raise ValueError("temperature must be between 0 and 1")

        return request

    @staticmethod
    def get_valid_model_names():
        valid_model_names = {"gpt-3.5-turbo", "gpt-3.5-turbo-16k", "gpt-4", "gpt-3.5-turbo-0613"}
        return valid_model_names

    @validator("model_name")
    def validate_model_name(cls, request):
        valid_model_names = cls.get_valid_model_names()

        if request not in valid_model_names:
            raise ValueError(f"invalid model name given - {request} , valid ones are {valid_model_names}")

        return request