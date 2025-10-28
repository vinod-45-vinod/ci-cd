import pytest
from httpx import AsyncClient
from main import app

@pytest.mark.asyncio
async def test_health_check():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"

@pytest.mark.asyncio
async def test_generate_pdf_endpoint():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post("/generate-pdf", json={"requestId": "test-123", "url": "https://example.com"})
        assert response.status_code == 200
        assert response.json()["status"] == "processing"

def test_parse_article():
    from main import parse_article
    html = """<html><body><article><h1>Test Article</h1><p>This is a test paragraph.</p>
    <aside class="ad">Advertisement</aside></article></body></html>"""
    cleaned_html, title = parse_article(html, "https://example.com")
    assert "Test Article" in title
    assert "test paragraph" in cleaned_html
    assert "Advertisement" not in cleaned_html