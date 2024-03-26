import json
import logging
from settings.settings import settings
from server.utils.errors import INTERNAL_SERVER_ERROR_HTTPEXCEPTION
from pydantic import BaseModel, Field
import sqlite3
from contextlib import contextmanager

@contextmanager
def get_db_connection(database_path):
    conn = sqlite3.connect(database_path)
    try:
        yield conn
    finally:
        conn.close()

class InvoiceBody(BaseModel):
    NoFacture: str = Field(..., description="Invoice number")
    Date: str = Field(..., description="Formatted Date of the invoice release. Date should be formatted as DD/MM/YYYY")
    Description: str = Field(..., description="Description of the invoice")
    TotalHT: str = Field(..., description="Total amount excluding tax")
    TVA: str = Field(..., description="Total amount of taxes")
    TotalTTC: str = Field(..., description="Total amount including all taxes")
    Monnaie: str = Field(..., description="The currency used. Should be only EUR or DOLLAR")
    Vendeur: str = Field(..., description="Name of the vendor")

database = "invoices.db"

def create_table():
    with get_db_connection(database) as conn:
        create_table_sql = """ CREATE TABLE IF NOT EXISTS invoices (
                                        id integer PRIMARY KEY AUTOINCREMENT,
                                        NoFacture text NOT NULL,
                                        Date text NOT NULL,
                                        Description text,
                                        TotalHT text,
                                        TVA text,
                                        TotalTTC text,
                                        Monnaie text,
                                        Vendeur text
                                    ); """
        conn.execute(create_table_sql)

def append_invoice(invoice: InvoiceBody)->None:
    with get_db_connection(database) as conn:
        sql = ''' INSERT INTO invoices(NoFacture,Date,Description,TotalHT,TVA,TotalTTC,Monnaie,Vendeur)
                  VALUES(?,?,?,?,?,?,?,?) '''
        conn.execute(sql, (invoice.NoFacture, invoice.Date, invoice.Description, invoice.TotalHT, invoice.TVA, invoice.TotalTTC, invoice.Monnaie, invoice.Vendeur))
        conn.commit()

def get_invoices_as_json()->json:
    with get_db_connection(database) as conn:
        conn.row_factory = sqlite3.Row  # This enables column access by name
        cur = conn.cursor()
        cur.execute("SELECT * FROM invoices")
        rows = cur.fetchall()
        
        # Convert rows to dict
        invoices = [dict(row) for row in rows]  # sqlite3.Row supports dict access
        
    return json.dumps(invoices, ensure_ascii=False, indent=4)


create_table()