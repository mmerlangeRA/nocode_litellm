from typing import List
from langchain_community.document_loaders import WebBaseLoader, PyPDFLoader,Docx2txtLoader
from langchain.docstore.document import Document
from server.utils.file_extension import get_file_extension

import requests

async def get_file_extension_from_url(url:str)->str:
    response = requests.head(url, allow_redirects=True)
    content_type = response.headers.get('Content-Type')
    print(content_type)
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
        # Add more mappings as needed
    }
    
    # Get the file extension based on the Content-Type
    return mime_type_to_extension.get(content_type, 'Unknown')


async def get_Documents_from_url(url:str)->List[Document]:
    file_extension = await get_file_extension_from_url(url)
    print(file_extension)
    if file_extension == '.pdf':
        loader = PyPDFLoader(url)
    elif file_extension == '.docx':
        loader = Docx2txtLoader(url)
    else:
        loader = WebBaseLoader(url)
    
    docs:List[Document] =  loader.load_and_split()
        
    return docs



""" 
    if True:
        if not file_extension == 'pdf':
            executor = BSQueryExecutor()
            query={
                "action":"find",
                }
            content.page_content = executor.query(url, content.page_content, query) 
"""