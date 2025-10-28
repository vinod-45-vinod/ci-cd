import pytest
import asyncio
from httpx import AsyncClient
from unittest.mock import patch, AsyncMock, MagicMock
from main import (
    app, parse_article, parse_wikipedia, parse_general_article,
    safe_get_text, fetch_html, notify_backend, process_pdf_generation
)

# ============================================================================
# UNIT TESTS
# ============================================================================

@pytest.mark.unit
def test_safe_get_text_with_valid_element():
    """Test safe_get_text with a valid BeautifulSoup element"""
    from bs4 import BeautifulSoup
    html = '<p>  Test content  </p>'
    element = BeautifulSoup(html, 'lxml').find('p')
    result = safe_get_text(element)
    assert result == 'Test content'

@pytest.mark.unit
def test_safe_get_text_with_none():
    """Test safe_get_text with None element"""
    result = safe_get_text(None)
    assert result == ''

@pytest.mark.unit
def test_safe_get_text_with_default():
    """Test safe_get_text with custom default value"""
    result = safe_get_text(None, 'default_value')
    assert result == 'default_value'

@pytest.mark.unit
def test_parse_wikipedia_basic():
    """Test Wikipedia parser with basic structure"""
    html = """
    <html>
        <head><title>Test Wikipedia Article</title></head>
        <body>
            <h1>Wikipedia Article Title</h1>
            <div id="mw-content-text">
                <div class="mw-parser-output">
                    <p>This is the main content of the Wikipedia article.</p>
                    <h2>Section Header</h2>
                    <p>Section content here.</p>
                </div>
            </div>
        </body>
    </html>
    """
    cleaned_html, title = parse_wikipedia(html)
    assert 'Wikipedia Article Title' in title or 'Test Wikipedia Article' in title
    assert 'main content' in cleaned_html
    assert 'Section Header' in cleaned_html

@pytest.mark.unit
def test_parse_wikipedia_removes_unwanted_elements():
    """Test that Wikipedia parser removes unwanted elements"""
    html = """
    <html>
        <body>
            <h1>Article Title</h1>
            <div id="mw-content-text">
                <p>Main content</p>
                <div class="navbox">Navigation content</div>
                <div class="infobox">Info box content</div>
                <span class="mw-editsection">Edit section</span>
            </div>
        </body>
    </html>
    """
    cleaned_html, _ = parse_wikipedia(html)
    assert 'Main content' in cleaned_html
    assert 'Navigation content' not in cleaned_html
    assert 'Info box content' not in cleaned_html
    assert 'Edit section' not in cleaned_html

@pytest.mark.unit
def test_parse_general_article_basic():
    """Test general article parser with basic structure"""
    html = """
    <html>
        <head><title>Test Article</title></head>
        <body>
            <article>
                <h1>Article Title</h1>
                <p>This is the main article content.</p>
                <h2>Subsection</h2>
                <p>More content here.</p>
            </article>
        </body>
    </html>
    """
    cleaned_html, title = parse_general_article(html)
    assert 'Article Title' in title
    assert 'main article content' in cleaned_html
    assert 'Subsection' in cleaned_html

@pytest.mark.unit
def test_parse_general_article_removes_unwanted():
    """Test that general parser removes unwanted elements"""
    html = """
    <html>
        <body>
            <article>
                <h1>Title</h1>
                <p>Content</p>
                <aside class="advertisement">Ad content</aside>
                <div class="sidebar">Sidebar</div>
                <nav>Navigation</nav>
                <script>alert('test');</script>
            </article>
        </body>
    </html>
    """
    cleaned_html, _ = parse_general_article(html)
    assert 'Content' in cleaned_html
    assert 'Ad content' not in cleaned_html
    assert 'Sidebar' not in cleaned_html
    assert 'Navigation' not in cleaned_html
    assert 'alert' not in cleaned_html

@pytest.mark.unit
def test_parse_article_wikipedia():
    """Test parse_article function with Wikipedia URL"""
    html = '<html><head><title>Wikipedia</title></head><body><h1>Test</h1><div id="mw-content-text"><p>Content</p></div></body></html>'
    url = 'https://en.wikipedia.org/wiki/Test'
    cleaned_html, title = parse_article(html, url)
    assert 'Test' in title or 'Wikipedia' in title
    assert 'Content' in cleaned_html

@pytest.mark.unit
def test_parse_article_general():
    """Test parse_article function with general URL"""
    html = '<html><head><title>Article</title></head><body><article><h1>Test</h1><p>Content</p></article></body></html>'
    url = 'https://example.com/article'
    cleaned_html, title = parse_article(html, url)
    assert 'Test' in title or 'Article' in title
    assert 'Content' in cleaned_html

# ============================================================================
# INTEGRATION TESTS
# ============================================================================

@pytest.mark.integration
@pytest.mark.asyncio
async def test_health_check():
    """Test health check endpoint"""
    async with AsyncClient(app=app, base_url='http://test') as client:
        response = await client.get('/health')
        assert response.status_code == 200
        data = response.json()
        assert data['status'] == 'healthy'
        assert data['service'] == 'PDF Generator'
        assert 'timestamp' in data
        assert 'pdf_output_dir' in data

@pytest.mark.integration
@pytest.mark.asyncio
async def test_root_endpoint():
    """Test root endpoint"""
    async with AsyncClient(app=app, base_url='http://test') as client:
        response = await client.get('/')
        assert response.status_code == 200
        data = response.json()
        assert 'message' in data
        assert 'version' in data
        assert 'endpoints' in data

@pytest.mark.integration
@pytest.mark.asyncio
async def test_generate_pdf_endpoint_valid():
    """Test PDF generation endpoint with valid request"""
    async with AsyncClient(app=app, base_url='http://test') as client:
        payload = {
            'requestId': 'test-123',
            'url': 'https://example.com/article'
        }
        response = await client.post('/generate-pdf', json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data['status'] == 'processing'
        assert data['requestId'] == 'test-123'
        assert 'message' in data

@pytest.mark.integration
@pytest.mark.asyncio
async def test_generate_pdf_endpoint_invalid_request_id():
    """Test PDF generation with invalid request ID"""
    async with AsyncClient(app=app, base_url='http://test') as client:
        payload = {
            'requestId': '',
            'url': 'https://example.com/article'
        }
        response = await client.post('/generate-pdf', json=payload)
        assert response.status_code == 400
        assert 'Invalid request ID' in response.json()['detail']

@pytest.mark.integration
@pytest.mark.asyncio
async def test_generate_pdf_endpoint_long_request_id():
    """Test PDF generation with overly long request ID"""
    async with AsyncClient(app=app, base_url='http://test') as client:
        payload = {
            'requestId': 'x' * 101,
            'url': 'https://example.com/article'
        }
        response = await client.post('/generate-pdf', json=payload)
        assert response.status_code == 400

@pytest.mark.integration
@pytest.mark.asyncio
async def test_generate_pdf_endpoint_missing_url():
    """Test PDF generation without URL"""
    async with AsyncClient(app=app, base_url='http://test') as client:
        payload = {'requestId': 'test-123'}
        response = await client.post('/generate-pdf', json=payload)
        assert response.status_code == 422

@pytest.mark.integration
@pytest.mark.asyncio
async def test_fetch_html_success():
    """Test HTML fetching with mocked response"""
    with patch('aiohttp.ClientSession.get') as mock_get:
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.text = AsyncMock(return_value='<html><body>Test</body></html>')
        mock_get.return_value.__aenter__.return_value = mock_response
        
        html = await fetch_html('https://example.com')
        assert 'Test' in html

@pytest.mark.integration
@pytest.mark.asyncio
async def test_fetch_html_http_error():
    """Test HTML fetching with HTTP error"""
    with patch('aiohttp.ClientSession.get') as mock_get:
        mock_response = AsyncMock()
        mock_response.status = 404
        mock_get.return_value.__aenter__.return_value = mock_response
        
        with pytest.raises(Exception):
            await fetch_html('https://example.com/notfound')

@pytest.mark.integration
@pytest.mark.asyncio
async def test_notify_backend_success():
    """Test backend notification with success"""
    with patch('aiohttp.ClientSession.post') as mock_post:
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_post.return_value.__aenter__.return_value = mock_response
        
        await notify_backend('test-123', '/path/to/pdf.pdf', 'completed')
        mock_post.assert_called_once()

@pytest.mark.integration
@pytest.mark.asyncio
async def test_notify_backend_failure():
    """Test backend notification handles failures gracefully"""
    with patch('aiohttp.ClientSession.post') as mock_post:
        mock_post.side_effect = Exception('Network error')
        
        await notify_backend('test-123', None, 'failed', 'Error message')

# ============================================================================
# SYSTEM TESTS
# ============================================================================

@pytest.mark.system
@pytest.mark.asyncio
async def test_process_pdf_generation_workflow():
    """Test complete PDF generation workflow"""
    with patch('main.fetch_html') as mock_fetch, \
         patch('main.generate_pdf_playwright') as mock_generate, \
         patch('main.notify_backend') as mock_notify, \
         patch('main.save_debug_files') as mock_debug:
        
        mock_fetch.return_value = '<html><body><article><h1>Test</h1><p>Content</p></article></body></html>'
        mock_generate.return_value = None
        mock_notify.return_value = None
        mock_debug.return_value = None
        
        await process_pdf_generation('test-123', 'https://example.com/article')
        
        mock_fetch.assert_called_once()
        mock_generate.assert_called_once()
        mock_notify.assert_called_once()

@pytest.mark.system
@pytest.mark.asyncio
async def test_process_pdf_generation_handles_errors():
    """Test PDF generation handles errors properly"""
    with patch('main.fetch_html') as mock_fetch, \
         patch('main.notify_backend') as mock_notify:
        
        mock_fetch.side_effect = Exception('Fetch error')
        mock_notify.return_value = None
        
        await process_pdf_generation('test-123', 'https://example.com/article')
        
        mock_notify.assert_called_once()
        call_args = mock_notify.call_args[0]
        assert call_args[0] == 'test-123'
        assert call_args[2] == 'failed'

@pytest.mark.system
def test_parse_article_handles_malformed_html():
    """Test parse_article with malformed HTML"""
    html = '<html><body><h1>Title<p>Unclosed tags'
    url = 'https://example.com'
    
    cleaned_html, title = parse_article(html, url)
    assert isinstance(cleaned_html, str)
    assert isinstance(title, str)

@pytest.mark.system
def test_parse_article_empty_content():
    """Test parse_article with minimal content"""
    html = '<html><head><title>Empty</title></head><body></body></html>'
    url = 'https://example.com'
    
    cleaned_html, title = parse_article(html, url)
    assert isinstance(cleaned_html, str)
    assert len(cleaned_html) > 0

@pytest.mark.system
def test_parse_wikipedia_with_complex_structure():
    """Test Wikipedia parser with complex real-world structure"""
    html = """
    <html>
        <head><title>Complex Wikipedia Article - Wikipedia</title></head>
        <body>
            <h1>Complex Article</h1>
            <div id="mw-content-text">
                <div class="mw-parser-output">
                    <div class="shortdescription">Short description</div>
                    <p>Lead paragraph with content.</p>
                    <h2>Main Section</h2>
                    <p>Section content with <a href="#">links</a>.</p>
                    <ul><li>List item 1</li><li>List item 2</li></ul>
                    <h3>Subsection</h3>
                    <p>More detailed content.</p>
                </div>
            </div>
        </body>
    </html>
    """
    cleaned_html, title = parse_wikipedia(html)
    
    assert 'Complex Article' in title
    assert 'Lead paragraph' in cleaned_html
    assert 'Main Section' in cleaned_html
    assert 'Section content' in cleaned_html

@pytest.mark.system
def test_parse_general_article_with_images():
    """Test general parser preserves images"""
    html = """
    <html>
        <body>
            <article>
                <h1>Article with Images</h1>
                <p>Some content</p>
                <img src="https://example.com/image.jpg" alt="Test image">
                <p>More content</p>
            </article>
        </body>
    </html>
    """
    cleaned_html, _ = parse_general_article(html)
    
    assert 'Some content' in cleaned_html
    assert 'https://example.com/image.jpg' in cleaned_html
    assert 'alt="Test image"' in cleaned_html

@pytest.mark.system
def test_multiple_parser_consistency():
    """Test that parsers consistently handle similar content"""
    html_template = '<html><body>{}<h1>Title</h1><p>Content paragraph.</p></body></html>'
    
    wiki_html = html_template.format('<div id="mw-content-text"><div class="mw-parser-output">')
    wiki_cleaned, wiki_title = parse_wikipedia(wiki_html)
    
    general_html = html_template.format('<article>')
    general_cleaned, general_title = parse_general_article(general_html)
    
    assert 'Title' in wiki_title
    assert 'Title' in general_title
    assert 'Content paragraph' in wiki_cleaned
    assert 'Content paragraph' in general_cleaned
