import io
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.routers.upload import extract_text_from_file

def test_extract_text_txt():
    content = b"Hello, ORBIT Batch 2 file upload testing!"
    extracted = extract_text_from_file(content, "test.txt")
    assert extracted == "Hello, ORBIT Batch 2 file upload testing!"

def test_upload_endpoint():
    client = TestClient(app)
    # 1. Establish session
    session_res = client.get("/session")
    assert session_res.status_code == 200

    # 2. Upload text file
    file_bytes = b"Sample document contents for prompt injection."
    files = {"file": ("sample.txt", io.BytesIO(file_bytes), "text/plain")}
    res = client.post("/upload", files=files)
    assert res.status_code == 200
    data = res.json()
    assert "document_id" in data
    assert data["filename"] == "sample.txt"
    assert data["text_length"] == len(file_bytes)

def test_upload_unsupported_extension():
    client = TestClient(app)
    client.get("/session")
    files = {"file": ("test.exe", io.BytesIO(b"binary data"), "application/octet-stream")}
    res = client.post("/upload", files=files)
    assert res.status_code == 400
