from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.routers import session, keys, chat, upload

app = FastAPI(title="ORBIT v1 Harness")

app.include_router(session.router)
app.include_router(keys.router)
app.include_router(chat.router)
app.include_router(upload.router)

@app.get("/health")
def health_check():
    return {"status": "ok"}

app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/", StaticFiles(directory="static", html=True), name="frontend")
