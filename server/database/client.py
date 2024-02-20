from supabase import create_client, Client
import uuid
from settings.settings import settings
from server.utils.errors import INTERNAL_SERVER_ERROR_HTTPEXCEPTION

def connect_to_supabase() -> Client:
    try:
        database_settings = settings().supabase
        url: str = database_settings.url
        key: str = database_settings.anon_key
        supabase: Client = create_client(url, key)
    except:
        raise INTERNAL_SERVER_ERROR_HTTPEXCEPTION("Could not connect with database")
    return supabase

def add_row_to_table(supabase: Client, table_name: str, data: dict)->None:
    error = supabase.table(table_name).insert(data).execute()
    if error:
        raise INTERNAL_SERVER_ERROR_HTTPEXCEPTION(str(error))
    else:
        print("Data inserted successfully.")

def get_new_service_id()->str:
    return uuid.uuid1()

def add_consumption(user_id:str,token_in: int, token_out:int, service_type:str, service_id:int, model:str)->None:
    supabase_client = connect_to_supabase()
    data = {
        "user_id": user_id,
        "token_in": token_in,
        "token_out": token_out,
        "service_type": service_type,
        "service_id": service_id,
        "model":model
    }
    add_row_to_table(supabase_client, "consumption", data)


