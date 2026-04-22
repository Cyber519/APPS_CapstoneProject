import sqlite3
from pathlib import Path

DB_PATH = Path("apps.db")

def init_db():
    from pathlib import Path
    schema_path = Path("database/schema.sql")
    conn = sqlite3.connect(DB_PATH)
    with open(schema_path, "r") as f:
        conn.executescript(f.read())
    conn.commit()
    conn.close()

def get_connection():
    conn = sqlite3.connect(DB_PATH, timeout=30)
    conn.row_factory = sqlite3.Row
    return conn