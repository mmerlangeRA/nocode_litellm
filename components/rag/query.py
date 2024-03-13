import os
import uuid
from components.rag import client
from chromadb.config import Settings
from chromadb.utils import embedding_functions
from settings.settings import settings
from server.tools.get_document_from_url import get_Documents_from_url


openai_ef = embedding_functions.OpenAIEmbeddingFunction(
                model_name="text-embedding-ada-002",api_key=settings().model_keys.openai
            )

collection = client.get_or_create_collection(name="test",embedding_function=openai_ef)

#needs more filtering
async def query_documents(query:str):
    results = collection.query(
        query_texts=[query],
        n_results=2
    )
    return results