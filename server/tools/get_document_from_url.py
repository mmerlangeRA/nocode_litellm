from langchain_community.document_loaders import WebBaseLoader, PyPDFLoader,Docx2txtLoader
from langchain.docstore.document import Document
from server.utils.file_extension import get_file_extension

async def get_document_from_url(url:str)->Document:
    file_extension = get_file_extension(url)
    
    if file_extension == 'pdf':
        loader = PyPDFLoader(url)
    elif file_extension == 'docx':
        loader = Docx2txtLoader(url)
    else:
        loader = WebBaseLoader(url)
    
    content:Document =  loader.load()
        
    return content


""" 
    if True:
        if not file_extension == 'pdf':
            executor = BSQueryExecutor()
            query={
                "action":"find",
                }
            content.page_content = executor.query(url, content.page_content, query) 
"""