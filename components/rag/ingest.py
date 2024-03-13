import os
import uuid
from components.rag import client
from chromadb.config import Settings
from chromadb.utils import embedding_functions
from settings.settings import settings
from server.tools.get_document_from_url import get_Documents_from_url
from server.database.client import add_row_to_table,supabase_client,add_rows_to_table
import tiktoken
import chromadb
import requests
import concurrent.futures
from typing import List
from concurrent.futures import ThreadPoolExecutor, as_completed

openai_ef = embedding_functions.OpenAIEmbeddingFunction(
                model_name="text-embedding-ada-002",api_key=settings().model_keys.openai
            )

collection = client.get_or_create_collection(name="test",embedding_function=openai_ef)


async def ingest_document(url:str, file_id:str, embeddingsProvider:str,user_id:str):
    encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")
    docs = await get_Documents_from_url(url)
    for doc in docs:
        doc.metadata["file_id"]=file_id
        doc.metadata["embeddingsProvider"]=embeddingsProvider

    infos = [doc.page_content for doc in docs]
    metadatas= [doc.metadata for doc in docs]
    ids = [uuid.uuid4().hex for doc in docs]
    print(metadatas)
    file_items=[]
    for doc in docs:
        file_item={
            "file_id":file_id,
            "user_id":user_id,
            "content":doc.page_content,
            "page":doc.metadata["page"],
            "tokens":encoding.encode(doc.pageContent).length
        }
        file_items.append(file_item)
    print(file_items)
    response =  add_rows_to_table("file_items",file_items)
    print(response)
    """     const file_items = chunks.map((chunk, index) => ({
        file_id,
        user_id: profile.user_id,
        content: chunk.content,
        tokens: chunk.tokens,
        openai_embedding:
            embeddingsProvider === "openai"
            ? ((embeddings[index] || null) as any)
            : null,
        local_embedding:
            embeddingsProvider === "local"
            ? ((embeddings[index] || null) as any)
            : null
        }))

        supabase_client  .from("file_items").upsert(file_items)

        const totalTokens = file_items.reduce((acc, item) => acc + item.tokens, 0)

        await supabaseAdmin
        .from("files")
        .update({ tokens: totalTokens })
        .eq("id", file_id) """

    collection.add(
        documents = infos,
        metadatas = metadatas,
        ids = ids
    )


def make_post_request(input_text: str, model: str, api_key: str) -> dict:
    url = "https://api.openai.com/v1/embeddings"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    payload = {
        "input": input_text,
        "model": model
    }
    response = requests.post(url, json=payload, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        return {"error": "Failed to fetch embeddings", "status_code": response.status_code}


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
            "embedding": self.embedding,
            "user_id": self.user_id,
            "page": self.page,
            "tokens": self.tokens
        }

def fetch_and_assign_embedding(file_item: FileItem, model: str, api_key: str):
    url = "https://api.openai.com/v1/embeddings"
    input_text = file_item.page_content
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    payload = {
        "input": input_text,
        "model": model
    }
    response = requests.post(url, json=payload, headers=headers)
    if response.status_code == 200:
        result= response.json()
        embedding = result['data'][0]['embedding']
    else:
        return {"error": "Failed to fetch embeddings", "status_code": response.status_code}
    if 'error' not in result:
        file_item.embedding = embedding  # Adjust this according to the actual structure of result


async def ingest_document_return_chunks(url:str, file_id:str, embeddingsProvider:str,user_id:str):
    embedding_api_key = settings().model_keys.openai
    model = "text-embedding-3-small" #text-embedding-3-small and text-embedding-3-large
    encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")
    docs = await get_Documents_from_url(url)
    file_items=[]
    for doc in docs:
        file_item=FileItem(file_id,doc.page_content,user_id,page=doc.metadata.get("page",0),tokens=len(encoding.encode(doc.page_content)))
        file_items.append(file_item)
    # Use ThreadPoolExecutor to process items in parallel
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        # Map each file_item to a future
        futures = [executor.submit(fetch_and_assign_embedding, item, model, embedding_api_key) for item in file_items]
        for future in as_completed(futures):
            try:
                # Result already processed in fetch_and_assign_embedding, but you can handle exceptions here
                future.result()
            except Exception as e:
                print(f"An error occurred: {e}")
    return [item.to_dict() for item in file_items]

