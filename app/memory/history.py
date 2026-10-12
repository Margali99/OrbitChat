from typing import List, Dict, Any
from app.db.store import (
    db_ensure_conversation,
    db_get_messages,
    db_save_message
)

def ensure_conversation(conversation_id: str, session_id: str, title: str = "New Conversation") -> str:
    db_ensure_conversation(conversation_id, session_id, title)
    return conversation_id

def get_conversation_history(conversation_id: str, limit: int = 20) -> List[Dict[str, Any]]:
    return db_get_messages(conversation_id, limit)

def save_message(conversation_id: str, role: str, content: str, model_used: str = None) -> None:
    db_save_message(conversation_id, role, content, model_used)
