import uuid
from fastapi import APIRouter, Request, Response
from app.db.store import db_create_session

router = APIRouter()

@router.get("/session")
def get_or_create_session(request: Request, response: Response):
    session_id = request.cookies.get("session_id")
    
    if not session_id:
        session_id = str(uuid.uuid4())
        db_create_session(session_id)
            
        response.set_cookie(
            key="session_id",
            value=session_id,
            httponly=True,
            samesite="lax"
        )
    
    return {"session_id": session_id}
