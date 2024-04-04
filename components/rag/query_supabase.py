import json
from langchain_community.vectorstores import SupabaseVectorStore
from langchain_openai import OpenAIEmbeddings

from server.database.client import SupabaseClient, add_row_to_table, connect_to_supabase
from settings.settings import settings
from components.rag.get_document_from_url import get_Documents_from_url
import tiktoken
from typing import List
from supabase.client import Client, create_client
from server.di import global_injector

embeddings = OpenAIEmbeddings()

vector_store = SupabaseVectorStore(
    embedding=embeddings,
    client=connect_to_supabase(),
    table_name="documents",
    query_name="match_documents",
)
#needs more filtering
async def query_documents(query:str,file_ids:List[str]):
    if file_ids :
        print("query_documents")
        print(file_ids)
        print(file_ids[0])
        filter0={"file_id": {"$eq": "4536cf56-76bf-4fbb-a65d-f9fcedb4980c"}}
        filter_jsonb = {
            "file_id": {"$in": file_ids}
        }

        results = vector_store.similarity_search(query, 1, filter=filter0)
    else :
        results =  vector_store.similarity_search(query, 1)
    print(results)
    return results