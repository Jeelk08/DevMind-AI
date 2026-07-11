from datetime import datetime

from app.database.connection import DatabaseConnection

class ConversationStore:
    def __init__(self):
        self.db = DatabaseConnection()
        self.create_tables()

    def create_tables(self):

        conn = self.db.get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sessions(
                id TEXT PRIMARY KEY,
                created_at TEXT
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS messages(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT,
                role TEXT,
                content TEXT,
                timestamp TEXT
            )
        """)
        conn.commit()
        conn.close()

    def save_message(self, session_id, role, content):
        conn = self.db.get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO messages(
                session_id, 
                role, 
                content,
                timestamp
                )
            VALUES (?, ?, ?, ?)
            """, 
        (
            session_id,
            role, 
            content,
            datetime.now().isoformat()
        ))
        conn.commit()
        conn.close()

    
    def get_history(self, session_id):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT role, content
            FROM messages
            WHERE session_id = ?
            ORDER BY id ASC
            """, (session_id,))
        
        rows = cursor.fetchall()
        
        conn.close()

        return [
            {
                "role": row["role"],
                "content": row["content"]
            }
            for row in rows
        ]
