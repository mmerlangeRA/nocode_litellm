from typing import List
from langchain_community.document_loaders import WebBaseLoader, PyPDFLoader,Docx2txtLoader
from langchain.docstore.document import Document
from server.utils.file_extension import get_file_extension

async def get_Documents_from_url(url:str)->List[Document]:
    file_extension = get_file_extension(url)
    
    if file_extension == 'pdf':
        loader = PyPDFLoader(url)
    elif file_extension == 'docx':
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