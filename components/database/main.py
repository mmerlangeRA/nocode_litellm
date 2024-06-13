import sqlite3
from typing import Generator

def get_db() -> Generator:
    conn = sqlite3.connect('files.db', check_same_thread=False)
    try:
        yield conn
    finally:
        conn.close()

def init_db():
    conn = sqlite3.connect('files.db')
    with conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS files (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_name TEXT NOT NULL
            )
        ''')
    conn.close()

def insert_file_record(conn: sqlite3.Connection, file_name: str) -> int:
    cursor = conn.cursor()
    cursor.execute('INSERT INTO files (file_name) VALUES (?)', (file_name,))
    id = cursor.lastrowid
    rows = cursor.fetchall()
    print("Showing rows")
    for row in rows:
        print(row)
    return id
