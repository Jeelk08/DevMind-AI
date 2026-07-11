import uuid
from datetime import datetime
from app.database.connection import DatabaseConnection

class SessionManager:
    def __init__(self):
        self.db = DatabaseConnection()

    def create_session(self):
        session_id = str(uuid.uuid4())
        
        conn = self.db.get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO sessions(
                       id, 
                       created_ai
            )
            VALUES (?, ?)
            """, (
                session_id,
                datetime.now().isoformat()
            ))
        
        conn.commit()
        conn.close()
        return session_id
    
    def session_exists(self, session_id):
        conn = self.db.get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id
            FROM sessions
            WHERE id = ?
            """, (session_id,))

        row = cursor.fetchone()

        conn.close()
        return row is not None
    
    
    def delete_session(self, session_id):
        conn = self.db.get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            DELETE FROM sessions 
            WHERE id = ?
            """, (session_id,))
        conn.commit()
        conn.close()