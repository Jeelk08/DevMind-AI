# app/database/connection.py

import sqlite3
from pathlib import Path

class DatabaseConnection:
    def __init__(self):
        self.db_path = Path(__file__).parent / "devmind.db"

    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    