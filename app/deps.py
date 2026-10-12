from fastapi import Request, HTTPException, status

def get_session_id(request: Request) -> str:
    session_id = request.cookies.get("session_id")
    if not session_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session cookie missing"
        )
    return session_id
