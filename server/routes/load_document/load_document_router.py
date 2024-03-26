import base64
import os
from typing import Literal
from uuid import uuid4
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from server.tools.get_document_from_url import get_Documents_from_url
from server.utils.errors import FORBIDDEN_HTTPEXCEPTION
from server.utils.tokens import UserRights, generate_token, verify_token
from settings.settings import settings


load_document_router = APIRouter(prefix="/v1")

def safe_base64_decode(data_str: str):
    padding_needed = len(data_str) % 4
    if padding_needed:  # Add necessary padding
        data_str += '=' * (4 - padding_needed)
    return base64.b64decode(data_str)

@load_document_router.post("/load", tags=["load document"])
async def load_doc_route(request: Request, current_user: dict = Depends(verify_token)) :
    doc = await get_Documents_from_url(request.body.url)

    return {"response":doc}

class uploadImageBody(BaseModel):
    data_url: str = Field(..., description="The data URL of the image")

@load_document_router.post("/uploadImage", tags=["load document"])
async def upload_image(request:Request,imageBody: uploadImageBody):
    print(imageBody)
    data_url= imageBody.data_url
    print(data_url)
    if not data_url.startswith("data:image/"):
            raise HTTPException(status_code=400, detail="Invalid image data URL")

    header, base64_data = data_url.split(",", 1)
    file_extension = header.split('/')[1].split(';')[0]  # Extract file extension from MIME type

    try:
        image_data = safe_base64_decode(base64_data)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Base64 decoding error: {e}")

    filename = f"{uuid4()}.{file_extension}"
    file_path = os.path.join("static", filename)

    try:
        os.makedirs("static", exist_ok=True)
        with open(file_path, "wb") as file:
            file.write(image_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving image: {e}")

    return JSONResponse(status_code=200, content={"message": "Image uploaded successfully", "filename": filename})
