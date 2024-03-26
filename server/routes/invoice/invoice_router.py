import os
from typing import Literal
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field
from components.invoices.invoice import InvoiceBody,append_invoice,get_invoices_as_json
from server.tools.get_document_from_url import get_Documents_from_url
from server.utils.errors import FORBIDDEN_HTTPEXCEPTION
from server.utils.tokens import UserRights, generate_token, verify_token
from settings.settings import settings


invoice_router = APIRouter(prefix="/v1/invoice")


@invoice_router.post("/", tags=["invoice"])
async def post_invoice_route(request:Request,invoiceRequest: InvoiceBody) :
    append_invoice(invoiceRequest)
    return {"response":"OK"}


@invoice_router.get("/", tags=["invoice"])
def getinvoices():
    return get_invoices_as_json()