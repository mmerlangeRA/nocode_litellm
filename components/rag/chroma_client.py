import chromadb
from chromadb.config import Settings
from settings.settings import settings
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings

chroma_settings = settings().chroma
collection_name=chroma_settings.collection_name
dockerized = chroma_settings.dockerized

print(f'collection_name is {collection_name}')
print(f'dockerized is {dockerized}')

if not dockerized:
    persist_directory="./"+settings().chroma.directory
    persistent_client = chromadb.PersistentClient(path=persist_directory)
else:
    persistent_client = chromadb.HttpClient(host="chroma", port = 8000, settings=Settings(allow_reset=True, anonymized_telemetry=False))


chroma_collection = persistent_client.get_or_create_collection(collection_name)

embedding_function = OpenAIEmbeddings()

langchain_chroma = Chroma(
    client=persistent_client,
    collection_name=collection_name,
    embedding_function=embedding_function,
)
