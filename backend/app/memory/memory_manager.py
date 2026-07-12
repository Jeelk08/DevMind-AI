from app.memory.conversation_store import ConversationStore
from app.memory.session_manager import SessionManager


class MemoryManager:
    def __init__(self):
        self.conversation_store = ConversationStore()
        self.session_manager = SessionManager()

    def create_session(self):
        return self.session_manager.create_session()

    def save_message(self,
                     session_id,
                     role,
                     content):
        return self.conversation_store.save_message(session_id, 
                                                    role, 
                                                    content)

    def get_history(self, session_id):
        return self.conversation_store.get_history(session_id)

    def clear_chat(self, session_id):
        self.conversation_store.delete_messages(session_id)
        self.session_manager.delete_session(session_id)
        