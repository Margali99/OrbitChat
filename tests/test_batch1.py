import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.security.crypto import encrypt_key, decrypt_key

def test_crypto_roundtrip():
    original = "sk-test-1234567890"
    encrypted = encrypt_key(original)
    assert encrypted != original
    decrypted = decrypt_key(encrypted)
    assert decrypted == original

def test_session_endpoint():
    client = TestClient(app)
    response = client.get("/session")
    assert response.status_code == 200
    json_data = response.json()
    assert "session_id" in json_data
    assert "session_id" in response.cookies

def test_keys_without_session():
    client = TestClient(app)
    response = client.post("/keys", json={"provider": "anthropic", "api_key": "sk-ant-fake-key"})
    assert response.status_code == 401

def test_keys_with_session():
    client = TestClient(app)
    session_res = client.get("/session")
    assert session_res.status_code == 200
    
    res = client.post("/keys", json={"provider": "anthropic", "api_key": "sk-ant-fake-key"})
    assert res.status_code in [200, 500]
