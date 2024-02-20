from typing import List, Optional
import uuid
from pydantic import BaseModel, Field
from server.database.client import add_user_consumption, create_service,finish_service
from server.utils.errors import INTERNAL_SERVER_ERROR_HTTPEXCEPTION
import logging
from enum import Enum

class ServiceTpes(Enum):
    Chat = "Chat"
    Scrap = "Scrap"
    Summarize = "Summarize"

logger = logging.getLogger(__name__)

class Consumption():
    token_in: int
    token_out: int
    model: str
    def __init__(self,token_in: int, token_out: int, model: str):
        self.token_in = token_in
        self.token_out = token_out
        self.model = model
        
class Service():
    service_id: Optional[int] = Field(default_factory=int)
    service_type: ServiceTpes
    consumptions: List[Consumption] = []
    user_id: uuid.UUID
    description: Optional[str] = "none"

    def __init__(self, service_type: str,user_id:str,description="none"):
        self.service_id = create_service(user_id,service_type,description=description)
        self.service_type = service_type
        self.user_id = user_id

    def add_consumption(self, token_in: int, token_out: int, model: str)->Consumption:
        self.consumptions.append(Consumption(token_in, token_out, model))
        add_user_consumption(self.user_id, token_in, token_out, self.service_type, self.service_id, model)
        return self.consumptions[-1]
    
    def finish(self):
        finish_service(self.service_id)