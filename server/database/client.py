from supabase import create_client, Client
import uuid
from settings.settings import settings
from server.utils.errors import INTERNAL_SERVER_ERROR_HTTPEXCEPTION
import logging
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

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
        return api_response.data[0].get("id")
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



def create_service(user_id:str,service_type:str,description:str)->int:
    data = {
        "user_id": user_id,
        "type": service_type,
        "description":description
    }
    return add_row_to_table("services", data)

def finish_service(service_id:uuid.UUID)->None:
    data = {
        "finished_at": datetime.now(timezone.utc),
    }
    update_row_to_table("services", service_id, data)
