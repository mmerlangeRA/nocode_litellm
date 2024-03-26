import io
import json
from typing import List
from supabase import create_client, Client
import uuid

from server.utils.errors import INTERNAL_SERVER_ERROR_HTTPEXCEPTION
import logging
from datetime import datetime, timezone
import base64
from httpx import AsyncClient

logger = logging.getLogger(__name__)


class SupabaseClient:
    def __init__(self,SUPABASE_URL,SUPABASE_KEY):
        self.url = SUPABASE_URL
        self.headers = {
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}",
            "Content-Type": "application/json",
        }
        self.client = AsyncClient(base_url=self.url, headers=self.headers)
    
    async def close(self):
        await self.client.aclose()

def get_supabase_client():
    return SupabaseClient()


'''
def connect_to_supabase() -> Client:
    try:
        database_settings = settings().supabase
        print(database_settings)
        url: str = database_settings.url
        key: str = database_settings.service_role_key
        supabase: Client = create_client(url, key)
    except:
        raise INTERNAL_SERVER_ERROR_HTTPEXCEPTION("Could not connect with database")
    return supabase


supabase_client = connect_to_supabase()


def add_row_to_table(table_name: str, data: dict)->int:
    try:
        api_response = supabase_client.table(table_name).insert(data).execute()
        logger.debug("Data inserted successfully in "+table_name)
        return api_response.data[0]
    except Exception as e:
        print(e)
        raise INTERNAL_SERVER_ERROR_HTTPEXCEPTION(e)

def add_rows_to_table(table_name: str, data: List[dict])->int:
    try:
        api_response = supabase_client.table(table_name).insert(data).execute()
        logger.debug("Data inserted successfully in "+table_name)
        return api_response.data
    except Exception as e:
        print(e)
        raise INTERNAL_SERVER_ERROR_HTTPEXCEPTION(e)
        

def update_row_to_table(table_name: str,id:uuid.UUID, data: dict)->int:
    try:
        api_response = supabase_client.table(table_name).update(data).eq('id', id).execute()
        logger.log("Data updated successfully in "+table_name)
        return api_response.data[0].get("id")
    except Exception as e:
        print(e)
        raise INTERNAL_SERVER_ERROR_HTTPEXCEPTION(e)



def add_user_consumption(user_id:str,token_in: int, token_out:int, service_type:str, service_id:int, model:str)->int:
    data = {
        "user_id": user_id,
        "token_in": token_in,
        "token_out": token_out,
        "service_type": service_type,
        "service_id": service_id,
        "model":model
    }
    return add_row_to_table("consumption", data)

def create_file():
    payload = {
    "user_id": "741f03fc-22bc-45f6-b9ba-4a3064893b64",
    "file_id": "summarized_articles.txt"
    }
    array_of_objects = [
    {"name": "Object1", "value": 123},
    {"name": "Object2", "value": 456},
    {"name": "Object3", "value": 789}
]

    path_on_supastorage = f"{payload['user_id']}/{base64.b64encode(payload['file_id'].encode()).decode()}"
    file_like_object = io.StringIO()

    # Write the array of objects as a pretty-printed JSON string to the in-memory file
    json.dump(array_of_objects, file_like_object, indent=4)

    # To simulate passing the file to another service, you might need to seek to the beginning
    file_like_object.seek(0)
    with open('output_pretty.txt', 'w') as file:
    # Dump the array of objects as a formatted JSON string
        json.dump(array_of_objects, file, indent=4)


    with open('output_pretty.txt', 'r') as file:
        print("path_on_supastorage")
        print(path_on_supastorage)
        supabase_client.storage.from_("files").upload(file='output_pretty.txt',path=path_on_supastorage, file_options={"content-type": "text/plain"})

# Simulate reading from this in-memory file (as another service might do)
    content = file_like_object.read()
    
        




def finish_service(service_id:uuid.UUID)->None:
    data = {
        "finished_at": datetime.now(timezone.utc),
    }
    update_row_to_table("services", service_id, data)
'''

def create_service(user_id:str,service_type:str,description:str)->int:
    # data = {
    #     "user_id": user_id,
    #     "type": service_type,
    #     "description":description
    # }
    # return add_row_to_table("services", data)
    return 0

def finish_service(service_id:uuid.UUID)->None:
    return

def add_row_to_table(table_name: str, data: dict)->int:
    return 0

def add_rows_to_table(table_name: str, data: List[dict])->int:
    return 0