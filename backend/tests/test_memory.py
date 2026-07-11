from app.memory.conversation_store import ConversationStore


store = ConversationStore()

session_id = "session_001"

store.save_message(
    session_id,
    "user",
    "hello"
)

store.save_message(
    session_id,
    "assistant",
    "Hi Jeel!"
)

store.save_message(
    session_id,
    "user",
    "How are you?"
)

history = store.get_history(session_id)

print(history)
