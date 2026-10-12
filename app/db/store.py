import uuid
from typing import List, Dict, Any, Optional
from app.db.supabase_client import get_supabase_client

MEMORY_SESSIONS = set()
MEMORY_KEYS: Dict[str, Dict[str, str]] = {}
MEMORY_CONVERSATIONS: Dict[str, Dict[str, Any]] = {}
MEMORY_MESSAGES: Dict[str, List[Dict[str, Any]]] = {}
MEMORY_DOCUMENTS: Dict[str, Dict[str, Any]] = {}

def db_create_session(session_id: str):
    MEMORY_SESSIONS.add(session_id)
    try:
        client = get_supabase_client()
        client.table("sessions").insert({"id": session_id}).execute()
    except Exception:
        pass

def db_save_key(session_id: str, provider: str, encrypted_key: str):
    p = provider.lower()
    if session_id not in MEMORY_KEYS:
        MEMORY_KEYS[session_id] = {}
    MEMORY_KEYS[session_id][p] = encrypted_key

    try:
        client = get_supabase_client()
        res = client.table("user_keys").select("id").eq("session_id", session_id).eq("provider", p).execute()
        if res.data:
            key_id = res.data[0]["id"]
            client.table("user_keys").update({"encrypted_key": encrypted_key}).eq("id", key_id).execute()
        else:
            client.table("user_keys").insert({
                "id": str(uuid.uuid4()),
                "session_id": session_id,
                "provider": p,
                "encrypted_key": encrypted_key
            }).execute()
    except Exception:
        pass

def db_get_keys(session_id: str) -> Dict[str, str]:
    keys = dict(MEMORY_KEYS.get(session_id, {}))
    try:
        client = get_supabase_client()
        res = client.table("user_keys").select("provider, encrypted_key").eq("session_id", session_id).execute()
        if res.data:
            for row in res.data:
                keys[row["provider"].lower()] = row["encrypted_key"]
    except Exception:
        pass
    return keys

def db_get_key(session_id: str, provider: str) -> Optional[str]:
    keys = db_get_keys(session_id)
    return keys.get(provider.lower())

def db_ensure_conversation(conversation_id: str, session_id: str, title: str = "New Conversation"):
    if conversation_id not in MEMORY_CONVERSATIONS:
        MEMORY_CONVERSATIONS[conversation_id] = {"id": conversation_id, "session_id": session_id, "title": title}
    try:
        client = get_supabase_client()
        res = client.table("conversations").select("id").eq("id", conversation_id).execute()
        if not res.data:
            client.table("conversations").insert({"id": conversation_id, "session_id": session_id, "title": title}).execute()
    except Exception:
        pass

def db_save_message(conversation_id: str, role: str, content: str, model_used: str = None):
    msg = {"id": str(uuid.uuid4()), "conversation_id": conversation_id, "role": role, "content": content, "model_used": model_used}
    if conversation_id not in MEMORY_MESSAGES:
        MEMORY_MESSAGES[conversation_id] = []
    MEMORY_MESSAGES[conversation_id].append(msg)
    try:
        client = get_supabase_client()
        client.table("messages").insert(msg).execute()
    except Exception:
        pass

def db_get_messages(conversation_id: str, limit: int = 20) -> List[Dict[str, Any]]:
    mem_msgs = MEMORY_MESSAGES.get(conversation_id, [])
    try:
        client = get_supabase_client()
        res = client.table("messages").select("role, content").eq("conversation_id", conversation_id).order("created_at", desc=False).limit(limit).execute()
        if res.data:
            return res.data
    except Exception:
        pass
    return mem_msgs[-limit:]

def db_save_document(doc_id: str, session_id: str, filename: str, extracted_text: str):
    MEMORY_DOCUMENTS[doc_id] = {"id": doc_id, "session_id": session_id, "filename": filename, "extracted_text": extracted_text}
    try:
        client = get_supabase_client()
        client.table("documents").insert({
            "id": doc_id, "session_id": session_id, "filename": filename, "extracted_text": extracted_text
        }).execute()
    except Exception:
        pass

def db_get_document(doc_id: str) -> Optional[Dict[str, Any]]:
    if doc_id in MEMORY_DOCUMENTS:
        return MEMORY_DOCUMENTS[doc_id]
    try:
        client = get_supabase_client()
        res = client.table("documents").select("extracted_text").eq("id", doc_id).execute()
        if res.data:
            return res.data[0]
    except Exception:
        pass
    return None
