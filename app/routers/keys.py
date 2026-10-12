from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException
from app.deps import get_session_id
from app.security.crypto import encrypt_key
from app.db.store import db_save_key, db_get_keys

router = APIRouter()

class KeyPayload(BaseModel):
    provider: str
    api_key: str

@router.post("/keys")
def store_key(payload: KeyPayload, session_id: str = Depends(get_session_id)):
    if not payload.api_key or not payload.api_key.strip():
        raise HTTPException(status_code=400, detail="API key cannot be empty")
        
    encrypted = encrypt_key(payload.api_key.strip())
    provider_name = payload.provider.lower()
    
    try:
        db_save_key(session_id, provider_name, encrypted)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    
    return {"status": "ok", "provider": provider_name}

@router.get("/keys")
def list_configured_keys(session_id: str = Depends(get_session_id)):
    keys = db_get_keys(session_id)
    return {"configured_providers": list(keys.keys())}
