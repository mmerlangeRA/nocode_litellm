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

class ProductBody(BaseModel):
    IdProduct: str = Field(..., description="Product id")
    Date: str = Field(..., description="Formatted Date of the product release. Date should be formatted as DD/MM/YYYY")
    Description: str = Field(..., description="Description of the product")
    TotalHT: str = Field(..., description="Total amount excluding tax")
    TVA: str = Field(..., description="Total amount of taxes")

database = "products.db"

def create_table():
    with get_db_connection(database) as conn:
        create_table_sql = """ CREATE TABLE IF NOT EXISTS products (
                                        id integer PRIMARY KEY AUTOINCREMENT,
                                        IdProduct text NOT NULL,
                                        Date text NOT NULL,
                                        Description text,
                                        TotalHT text,
                                        TVA text
                                    ); """
        conn.execute(create_table_sql)

def append_product(product: ProductBody)->None:
    with get_db_connection(database) as conn:
        sql = ''' INSERT INTO products(IdProduct,Date,Description,TotalHT,TVA)
                  VALUES(?,?,?,?,?) '''
        conn.execute(sql, (product.IdProduct, product.Date, product.Description, product.TotalHT, product.TVA))
        conn.commit()

def get_products_as_json()->json:
    with get_db_connection(database) as conn:
        conn.row_factory = sqlite3.Row  # This enables column access by name
        cur = conn.cursor()
        cur.execute("SELECT * FROM products")
        rows = cur.fetchall()
        
        # Convert rows to dict
        products = [dict(row) for row in rows]  # sqlite3.Row supports dict access
        
    return json.dumps(products, ensure_ascii=False, indent=4)


create_table()