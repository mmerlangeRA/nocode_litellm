import base64
import io
import json
from fastapi import HTTPException, UploadFile
from pydantic import BaseModel
from  components.workspaces.manage_workspaces import createFileWorkspace
from server.utils.errors import INTERNAL_SERVER_ERROR_HTTPEXCEPTION, PAYLOAD_TOO_LARGE_HTTPEXCEPTION
from server.database.client import add_row_to_table,supabase_client,get_row_from_table

class createFileRequet(BaseModel):
  name: str
  file: FileExistsError
  workspace_id: str
  embeddingsProvider: str 

from sqlalchemy import create_engine, Column, String, Integer, DateTime, ForeignKey, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime

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
    response = supabase_client.storage.from_("files").upload(storage_path, content)
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




