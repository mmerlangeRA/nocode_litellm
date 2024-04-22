import chromadb
from chromadb.config import Settings
from settings.settings import settings
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings

collection_name=settings().chroma.collection_name
print(f'collection_name is {collection_name}')

persistent_client = chromadb.HttpClient(host="chroma", port = 8000, settings=Settings(allow_reset=True, anonymized_telemetry=False))

chroma_collection = persistent_client.get_or_create_collection(collection_name)

embedding_function = OpenAIEmbeddings()

print(f"stetting up langchain_chroma with {collection_name}")
langchain_chroma = Chroma(
    client=persistent_client,
    collection_name=collection_name,
    embedding_function=embedding_function,
)
