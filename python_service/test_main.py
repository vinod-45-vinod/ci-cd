import pytest
from httpx import AsyncClient
from main import app, parse_general_article

@pytest.mark.asyncio
async def test_generate_pdf_with_wikipedia_india():
    """Test PDF generation endpoint with Wikipedia India URL"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        test_url = "https://en.wikipedia.org/wiki/India"
        response = await client.post(
            "/generate-pdf",
            json={"requestId": "test-wiki-india", "url": test_url}
        )
        # Endpoint should return 200 and processing status immediately
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "processing"
        assert data["requestId"] == "test-wiki-india"


def test_parse_general_article_basic():
    """Test HTML parsing logic for general articles"""
    html = """
    <html>
      <head><title>Test Article</title></head>
      <body>
        <h1>Heading</h1>
        <p>This is test content for unit testing.</p>
      </body>
    </html>
    """

    cleaned_html, title = parse_general_article(html)

    assert isinstance(cleaned_html, str)
    assert 'Test Article' in title or 'Heading' in cleaned_html
    assert '<p' in cleaned_html