import os
from typing import Literal
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field
from server.utils.errors import FORBIDDEN_HTTPEXCEPTION
from server.utils.tokens import UserRights, generate_token, verify_token
from fastapi.responses import HTMLResponse
from settings.settings import settings


public_files_router = APIRouter(prefix="/v1/public")


@public_files_router.get("/", tags=["public"])
async def list_files():
    static_folder_path = "static"  # Update this path to your static folder
    static_url_path = "/static"
    files = os.listdir(static_folder_path)
    html_content = "<html><body><h2>List of Files</h2><ul>"
    for file in files:
        file_path = f"{static_url_path}/{file}"
        html_content += f'<li><a href="{file_path}" download="{file}">{file}</a></li>'
    html_content += "</ul></body></html>"
    return HTMLResponse(content=html_content)

