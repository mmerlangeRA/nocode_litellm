import os
import re
from typing import List
import uuid
from langchain_community.document_loaders import WebBaseLoader, PyPDFLoader,Docx2txtLoader,UnstructuredPowerPointLoader, UnstructuredPDFLoader
from server.utils.errors import BAD_REQUEST_HTTPEXCEPTION, INTERNAL_SERVER_ERROR_HTTPEXCEPTION
from server.utils.file_extension import get_file_extension
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents.base import Document
import requests

def clean_text(text):
    # Remove hyphenation at line breaks
    text = re.sub(r'(\w+)-\n(\w+)', r'\1\2', text)
    # Remove line breaks within paragraphs
    text = re.sub(r'(?<!\n)\n(?!\n)', ' ', text)
    # Handle special characters and other common OCR issues here as needed
    return text

async def get_file_extension_from_url(url:str)->str:
    response = requests.head(url, allow_redirects=True)

    content_type = response.headers.get('Content-Type')
    # Map common MIME types to file extensions
    # This is a basic mapping; you may need to expand it based on your needs
    mime_type_to_extension = {
        'application/pdf': '.pdf',
        'image/jpeg': '.jpg',
        'image/png': '.png',
        'text/html': '.html',
        'text/plain': '.txt',
        'application/zip': '.zip',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document': '.docx',
        'application/vnd.openxmlformats-officedocument.presentationml.presentation': '.pptx'
        # Add more mappings as needed
    }
    
    # Get the file extension based on the Content-Type
    return mime_type_to_extension.get(content_type, 'Unknown')

def download_doc(url:str, local_filename:str)->str:
    with requests.get(url, stream=True) as r:
        r.raise_for_status()  # This will raise an exception for HTTP errors.
        with open(local_filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
    return local_filename


async def get_Documents_from_url(url:str,file_name:str,chunk_size=1000,chunk_overlap=50)->List[Document]:
    try:
        file_extension =  get_file_extension(file_name)
        extension_to_loader = {
            'pdf':UnstructuredPDFLoader,
            'docx': Docx2txtLoader,
            'pptx': UnstructuredPowerPointLoader,
            'html': WebBaseLoader
        }
        print(f'file_extension is {file_extension}')
        current_working_directory = os.getcwd()
        tmp_directory = os.path.join(current_working_directory, "tmp")
        isExist = os.path.exists(tmp_directory)
        if not isExist:
            os.makedirs(tmp_directory)
        tmp_file_name= str(uuid.uuid1())+ "_"+file_name
        tmp_file_path = os.path.join(tmp_directory, tmp_file_name)
        print("downloading "+url)
        url_to_use= download_doc(url, tmp_file_path)
        print(f"url_to_use {url_to_use}")
        loader_function = extension_to_loader.get(file_extension)
        
        if loader_function is None:
            raise BAD_REQUEST_HTTPEXCEPTION("Unsupported extention")
        loader = loader_function(url_to_use)
        documents:List[Document] = loader.load()

        #Clean text a bit
        #print(documents)
        print(f"now cleaning many {len(documents)}")
        for document in documents:
            print(document.page_content)
            document.page_content = clean_text(document.page_content)
            print(document.page_content)

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            is_separator_regex=False,
        )
        docs = text_splitter.split_documents(documents)
        if os.path.exists(tmp_file_path):
            os.remove(tmp_file_path) 
        print("nb docs", len(docs))
        return docs
    except Exception as e:
        print(e)
        raise INTERNAL_SERVER_ERROR_HTTPEXCEPTION(e)


async def get_Documents_from_local_path(local_path:str,file_name:str,chunk_size=1000,chunk_overlap=50)->List[Document]:
    try:
        file_extension =  get_file_extension(file_name)
        extension_to_loader = {
            'pdf':UnstructuredPDFLoader,
            'docx': Docx2txtLoader,
            'pptx': UnstructuredPowerPointLoader,
            'html': WebBaseLoader
        }
        print(f'file_extension is {file_extension}')
    
        loader_function = extension_to_loader.get(file_extension)
        
        if loader_function is None:
            raise BAD_REQUEST_HTTPEXCEPTION("Unsupported extention")
        loader = loader_function(local_path)
        documents:List[Document] = loader.load()

        #Clean text a bit
        #print(documents)
        print(f"now cleaning many {len(documents)}")
        for document in documents:
            #print(document.page_content)
            document.page_content = clean_text(document.page_content)
            #print(document.page_content)

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            is_separator_regex=False,
        )
        docs = text_splitter.split_documents(documents)
        print("nb docs", len(docs))
        return docs
    except Exception as e:
        print(e)
        raise INTERNAL_SERVER_ERROR_HTTPEXCEPTION(e)
