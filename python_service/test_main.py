import pytest
from httpx import AsyncClient
from main import app

@pytest.mark.asyncio
async def test_generate_pdf_with_wikipedia_india():
    """Test PDF generation with Wikipedia India URL"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        test_url = "https://en.wikipedia.org/wiki/India"
        response = await client.post(
            "/generate-pdf",
            json={"requestId": "test-wiki-india", "url": test_url}
        )
        assert response.status_code == 200
        assert response.json()["status"] == "processing"