from langchain_community.vectorstores import SupabaseVectorStore
from langchain_openai import OpenAIEmbeddings

from server.database.client import SupabaseClient, add_row_to_table, connect_to_supabase
from settings.settings import settings
from components.rag.get_document_from_url import get_Documents_from_url
import tiktoken
from typing import List
from supabase.client import Client, create_client
from server.di import global_injector


supabase: Client = global_injector.get(SupabaseClient).client
print(supabase)
embeddings = OpenAIEmbeddings()

vector_store = SupabaseVectorStore(
    embedding=embeddings,
    client=connect_to_supabase(),
    table_name="documents",
    query_name="match_documents",
)

async def ingest_document(url:str, file_id:str, file_name:str,embeddingsProvider:str,user_id:str):
    print("ingest_document "+file_name)
    encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")
    docs = await get_Documents_from_url(url,file_name)
    #print("docs generated",len(docs))
    for d in docs:
        d.metadata["file_id"] = file_id
        d.metadata["user_id"] = user_id
        d.metadata["source"]=""

    vector_store.add_texts(
        texts=[d.page_content for d in docs],
        metadatas=[d.metadata for d in docs],
    ) 
   

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
