import logging
import os
import uuid
from components.rag.get_document_from_url import get_Documents_from_local_path, get_Documents_from_url
from components.rag.chroma_client import persistent_client, chroma_collection,langchain_chroma
from os import listdir
from os.path import isfile, join

from components.database.main import insert_file_record

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

collection = chroma_collection

def delete_collection(collection_name:str)->bool:
    persistent_client.delete_collection(collection_name)
    persistent_client.close()
    print("collection deleted")
    return True

def delete_chunks_by_file_id(file_id:str):
    logger.debug(f"in delete_chunks_by_file_id {file_id}")
    ids_to_delete=[]
    query_where = {"file_id": file_id}
    docs = collection.get( where=query_where)
    logger.debug(docs)

    ids_to_delete = docs.get("ids") or []
    logger.debug(ids_to_delete)
    if(len(ids_to_delete)==0):
        return True
    
    collection.delete(ids=ids_to_delete)
    logger.debug("chunks deleted")
    return True

async def ingest_folder(folder_name,db, user_id="me"):

    mypath=os.path.join(os.getcwd(),folder_name)

    print(f'mypath is {mypath}')
    onlyfiles = [os.path.join(mypath,f) for f in listdir(mypath) if isfile(join(mypath, f))]
    for file_path in onlyfiles:
        print(f'file_path is {file_path}')
       
        file_name=os.path.basename(file_path)
        file_id= insert_file_record(db,file_name)
        docs = await get_Documents_from_local_path(file_path,file_name)
         #logger.debug(docs)
        ids=[]
        print("docs generated",len(docs))
        for d in docs:
            d.metadata["file_id"] = file_id
            d.metadata["user_id"] = user_id
            id = str(uuid.uuid1())
            ids.append(id)
            d.metadata["id"] = id
            d.metadata["source"] = ""

        langchain_chroma.add_texts(
            texts=[d.page_content for d in docs],
            metadatas=[d.metadata for d in docs],
            ids=ids
        ) 

async def ingest_document(url:str, file_id:str, file_name:str,embeddingsProvider:str,user_id:str):
    logger.debug("ingest_document "+file_name)
    #encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")
    docs = await get_Documents_from_url(url,file_name)
    #logger.debug(docs)
    ids=[]
    print("docs generated",len(docs))
    for d in docs:
        d.metadata["file_id"] = file_id
        d.metadata["user_id"] = user_id
        id = str(uuid.uuid1())
        ids.append(id)
        d.metadata["id"] = id
        d.metadata["source"] = ""

    langchain_chroma.add_texts(
        texts=[d.page_content for d in docs],
        metadatas=[d.metadata for d in docs],
        ids=ids
    ) 
    #logger.debug("There are", langchain_chroma._collection.count(), "in the collection")
   

class FileItem:
    def __init__(self, file_id:str,page_content: str,user_id:str,embedding= None, page = 0, tokens=0):
        self.file_id = file_id
        self.page_content = page_content
        self.embedding = embedding  
        self.user_id=user_id
        self.page=page
        self.tokens=tokens
    def to_dict(self):
        return {
            "file_id": self.file_id,
            "content": self.page_content,
            "openai_embedding": self.embedding,
            "user_id": self.user_id,
            "page": self.page,
            "tokens": self.tokens
        }
