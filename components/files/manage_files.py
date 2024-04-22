import base64
import logging
from fastapi import HTTPException, UploadFile
from pydantic import BaseModel
from  components.workspaces.manage_workspaces import createFileWorkspace
from server.utils.errors import INTERNAL_SERVER_ERROR_HTTPEXCEPTION, PAYLOAD_TOO_LARGE_HTTPEXCEPTION
from server.database.client import add_row_to_table,get_supabase_client

from sqlalchemy import create_engine, Column, String, Integer, DateTime, ForeignKey, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
from settings.settings import settings

logger = logging.getLogger(__name__)

Base = declarative_base()

table_name = "files"


class FileCreationRequest(BaseModel):

    description:str
    file_path: str
    name: str
    size:int
    tokens:int
    type : str
    user_id: str


async def upload_file(file: UploadFile,payload: dict):
    SIZE_LIMIT = 10000000  # 10MB
    user_id = payload['user_id']
    file_id = payload['file_id']
    # Convert file_id to a base64 string
    file_id_base64 = base64.urlsafe_b64encode(file_id.encode()).decode()
    storage_path = f"{user_id}/{file_id_base64}/{file.filename}"

    # Read file content
    content = await file.read()
    if len(content) > SIZE_LIMIT:
        raise PAYLOAD_TOO_LARGE_HTTPEXCEPTION(detail=f"File must be less than {SIZE_LIMIT / 1000000}MB")
    
    # Upload file to Supabase
    response = get_supabase_client().storage.from_("files").upload(storage_path, content)
    if 'error' in response and response['error']:
        raise INTERNAL_SERVER_ERROR_HTTPEXCEPTION(detail="Error uploading file to Supabase")

    return storage_path

'''
payload = {
    "name": "example.txt",
    "user_id": "user123",
    "file_id": "file456"
}
'''
async def create_file(file: UploadFile, fileRecord:FileCreationRequest, workspace_id:str,embeddingsProvider:str ):

    createdFile = add_row_to_table("files",fileRecord)

    await createFileWorkspace(user_id=createdFile["user_id"],file_id=createdFile[id],workspace_id= workspace_id)
    
    storage_path = await upload_file(file)

    #fetchedFile = await getFileById(createdFile.id)

    return createdFile


def getFileByUrl(file_id:str):
    logger.debug("getFileByUrl",file_id)
    supabase_url = settings().supabase.url
    supabase_key =settings().supabase.anon_key
    logger.debug(supabase_url, supabase_key)
    res= get_supabase_client(supabase_url,supabase_key).storage.from_('files').create_signed_url(file_id,60 * 60 * 24)
    logger.debug(res)
    return res


def fetch_row_by_id(table_name, row_id):
    """
    Fetch a row from a specified table in Supabase by ID.

    :param supabase_client: Initialized Supabase client
    :param table_name: Name of the table to query (str)
    :param row_id: ID of the row to fetch (int or str)
    :return: Row data as a dictionary or None if not found
    """
    print(f'fetch_row_by_id {table_name} with id={row_id}')
    supabase_url = settings().supabase.url
    supabase_key =settings().supabase.anon_key
    data = get_supabase_client(supabase_url,supabase_key).table(table_name).select("*").eq('id', row_id).execute()
    print("DATA below")
    results = data.data
    if results:
        return results[0]  # Return the first row if available
    else:
        print("No data found for the given ID.")
        return None


