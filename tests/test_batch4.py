from fastapi.testclient import TestClient
from app.main import app

def test_frontend_serving():
    client = TestClient(app)
    response = client.get("/")
    assert response.status_code == 200
    assert "Margali's Orbit" in response.text
    assert "model-select" in response.text

def test_static_css_js():
    client = TestClient(app)
    css_res = client.get("/static/style.css")
    assert css_res.status_code == 200
    assert "F8F9FD" in css_res.text

    js_res = client.get("/static/app.js")
    assert js_res.status_code == 200
    assert "initSession" in js_res.text
