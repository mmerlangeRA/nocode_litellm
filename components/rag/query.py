from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from components.files.manage_files import get_file_info
from server.utils.errors import NOT_FOUND_HTTPEXCEPTION
from typing import Dict, List, NamedTuple
from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import LLMChainExtractor
from langchain_core.documents.base import Document
from components.rag.chroma_client import chroma_collection,langchain_chroma

def transform_documents_to_json(documents: List[Document]) -> List[Dict[str, any]]:
    return [
        {
            "content": doc.page_content,
            "user_id": doc.metadata['user_id'],
            "file_id": doc.metadata['file_id'],
            "page": doc.metadata.get('page', -1),
            "id":doc.metadata.get('id', -1)
        } for doc in documents
    ]


""" llm = OpenAI(temperature=0)
compressor = LLMChainExtractor.from_llm(llm)
compression_retriever = ContextualCompressionRetriever(base_compressor=compressor, base_retriever=retriever)
 """

collection = chroma_collection


#needs more filtering
async def query_documents(query:str,source_count:int = 10, min_confidence = 0.2, file_ids:List[str]=[]):
    print(f'query: {query}')
    if file_ids and len(file_ids)>0:
        filter = {"file_id": {"$in": file_ids}}
        results = langchain_chroma.similarity_search_with_score(query, source_count, filter=filter)
    else :
        results =  langchain_chroma.similarity_search_with_score(query, source_count)
    print(results)

    filtered_docs = [doc for doc, score in results if score > min_confidence]
    print(f'returning {len(filtered_docs)} chunks confidence is {min_confidence}')
    #print(filtered_docs)
    #print(transform_documents_to_json(filtered_docs))
    return transform_documents_to_json(filtered_docs)

def get_chunk_by_id(id:str):
    chunks = collection.get(ids=[id])
    if len(chunks) == 0:
        raise NOT_FOUND_HTTPEXCEPTION(f"No chunk found with id {id}")
    id =  chunks.get("ids")[0]
    metadatas =  chunks.get("metadatas")[0]
    file_id =  metadatas.get("file_id")
    page =  metadatas.get("page",-1)
    content= chunks.get("documents")[0]
    return {"id":id,"file_id":file_id,"page":page,"content":content}

def get_chunk_file_id_and_page_by_id(id:str):
    chunk = collection.get(ids=[id])
    if len(chunk) == 0:
        print(f"No chunk found with id {id}")
        raise NOT_FOUND_HTTPEXCEPTION(f"No chunk found with id {id}")
    print(chunk)
    metadatas =  chunk.get("metadatas")[0]
    file_id =  metadatas.get("file_id")
    file_info = get_file_info(file_id)
    page =  metadatas.get("page",-1)
    return {"file_name":file_info.get('name'),"page":page, "file_path":file_info.get('file_path')}

def get_all_chunks():
    print("get_all_chunks ")
    return collection.get()

