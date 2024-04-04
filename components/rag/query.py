import json
import chromadb
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from settings.settings import settings
from typing import List
from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import LLMChainExtractor


""" llm = OpenAI(temperature=0)
compressor = LLMChainExtractor.from_llm(llm)
compression_retriever = ContextualCompressionRetriever(base_compressor=compressor, base_retriever=retriever)
 """
persist_directory="./"+settings().chroma.directory
collection_name=settings().chroma.collection_name
persistent_client = chromadb.PersistentClient(path=persist_directory)
collection = persistent_client.get_or_create_collection(collection_name)

embedding_function = OpenAIEmbeddings()

langchain_chroma = Chroma(
    client=persistent_client,
    collection_name=collection_name,
    embedding_function=embedding_function,
)
#needs more filtering
async def query_documents(query:str,source_count:int = 3, file_ids:List[str]=[]):
    if file_ids and len(file_ids)>0:
        #print("query_documents chromadb")
        filter = {"file_id": {"$in": file_ids}}
        #print(filter)
        results = langchain_chroma.similarity_search(query, source_count, filter=filter)
    else :
        results =  langchain_chroma.similarity_search(query, source_count)
    print(results)

    return results

def get_chunk_by_id(id:str):
    print("get_chunk_by_id ",id)
    return collection.get(ids=[id])

def get_all_chunks():
    print("get_all_chunks ")
    return collection.get()

#test = get_chunk_by_id("8ea710fa-f1d2-11ee-bb59-7e41e96a0b40")
#"594f147c-f1d5-11ee-975d-7e41e96a0b40"
#print(test)

#aall = get_all_chunks()
#"594f147c-f1d5-11ee-975d-7e41e96a0b40"
#print(aall)

'''
 ['4ce31246-f1b3-11ee-a43d-7e41e96a0b40', '594f15d0-f1d5-11ee-975d-7e41e96a0b40', '8611b69e-f1b3-11ee-8b09-7e41e96a0b40', '8ea710fa-f1d2-11ee-bb59-7e41e96a0b40', '8ea71118-f1d2-11ee-bb59-7e41e96a0b40', '95c8432c-f1b4-11ee-9efb-7e41e96a0b40', '98539328-f1c1-11ee-97d1-7e41e96a0b40', '98539350-f1c1-11ee-97d1-7e41e96a0b40', '994bf9e8-f1b5-11ee-a6b0-7e41e96a0b40', 'd53dfe06-f1b5-11ee-8846-7e41e96a0b40', 'd8a7022c-f1bf-11ee-9dbf-7e41e96a0b40', 'd8a702ae-f1bf-11ee-9dbf-7e41e96a0b40', 'deee6c60-f1b5-11ee-8846-7e41e96a0b40', 'ea2196fe-f1bd-11ee-88b0-7e41e96a0b40', 'ea21979e-f1bd-11ee-88b0-7e41e96a0b40', 'ea2197c6-f1bd-11ee-88b0-7e41e96a0b40', 'ea2197da-f1bd-11ee-88b0-7e41e96a0b40', 'ea2197f8-f1bd-11ee-88b0-7e41e96a0b40', 'ea219816-f1bd-11ee-88b0-7e41e96a0b40', 'ea21983e-f1bd-11ee-88b0-7e41e96a0b40', 'ea21985c-f1bd-11ee-88b0-7e41e96a0b40', 'ea21987a-f1bd-11ee-88b0-7e41e96a0b40', 'ea21988e-f1bd-11ee-88b0-7e41e96a0b40', 'ea2198a2-f1bd-11ee-88b0-7e41e96a0b40', 'f12cf48e-f1bd-11ee-88b0-7e41e96a0b40', 'f12cf4fc-f1bd-11ee-88b0-7e41e96a0b40', 'f12cf51a-f1bd-11ee-88b0-7e41e96a0b40', 'f12cf538-f1bd-11ee-88b0-7e41e96a0b40', 'f12cf54c-f1bd-11ee-88b0-7e41e96a0b40', 'f12cf560-f1bd-11ee-88b0-7e41e96a0b40', 'f8ac6c76-f1bd-11ee-88b0-7e41e96a0b40', 'f8ac6cee-f1bd-11ee-88b0-7e41e96a0b40', 'f8ac6d0c-f1bd-11ee-88b0-7e41e96a0b40', 'f8ac6d20-f1bd-11ee-88b0-7e41e96a0b40', 'f8ac6d3e-f1bd-11ee-88b0-7e41e96a0b40', 'f8ac6d52-f1bd-11ee-88b0-7e41e96a0b40', 'f8ac6d66-f1bd-11ee-88b0-7e41e96a0b40', 'fcb438da-f1b8-11ee-b448-7e41e96a0b40', 'fd590282-f1bf-11ee-bf51-7e41e96a0b40', 'fd590304-f1bf-11ee-bf51-7e41e96a0b40', 'ffb59dcc-586f-486b-8fbf-06a04863aeb2']
'''