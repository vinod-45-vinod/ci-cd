from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel, HttpUrl
from typing import Optional
import asyncio
import aiohttp
import os
import logging
from datetime import datetime
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright
import re
from collections import Counter

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(title="Article PDF Generator Service", version="1.0.0")

PDF_OUTPUT_DIR = os.getenv("PDF_OUTPUT_DIR", "./pdfs")
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:5000")

# Create directories
os.makedirs(PDF_OUTPUT_DIR, exist_ok=True)
os.makedirs(os.path.join(PDF_OUTPUT_DIR, 'debug'), exist_ok=True)

class PDFRequest(BaseModel):
    requestId: str
    url: HttpUrl

class PDFResponse(BaseModel):
    status: str
    requestId: str
    message: Optional[str] = None

def safe_get_text(element, default=""):
    """Safely get text from an element that might be None"""
    if element and hasattr(element, 'get_text'):
        return element.get_text(strip=True)
    return default

async def fetch_html(url: str) -> str:
    """Fetch HTML content from URL with proper error handling"""
    timeout = aiohttp.ClientTimeout(total=30)
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
    }
    
    try:
        async with aiohttp.ClientSession(timeout=timeout, headers=headers) as session:
            async with session.get(url) as response:
                if response.status != 200:
                    raise HTTPException(
                        status_code=400, 
                        detail=f"HTTP {response.status}: Failed to fetch URL"
                    )
                
                content = await response.text()
                logger.info(f"Fetched {len(content)} characters from URL")
                return content
                
    except aiohttp.ClientError as e:
        logger.error(f"Network error fetching HTML: {e}")
        raise HTTPException(status_code=400, detail=f"Network error: {str(e)}")
    except asyncio.TimeoutError:
        logger.error("Timeout fetching HTML")
        raise HTTPException(status_code=400, detail="Request timeout")
    except Exception as e:
        logger.error(f"Unexpected error fetching HTML: {e}")
        raise HTTPException(status_code=400, detail=f"Failed to fetch URL: {str(e)}")

def parse_wikipedia(html: str) -> tuple[str, str]:
    """Special parser for Wikipedia pages"""
    soup = BeautifulSoup(html, 'lxml')
    
    # Extract title safely
    title_element = soup.find('h1') or soup.find('title')
    title_text = safe_get_text(title_element, "Wikipedia Article")
    
    logger.info(f"Wikipedia article title: {title_text}")
    
    # Find the main content area - Wikipedia specific
    content_selectors = [
        '#mw-content-text',
        '.mw-parser-output',
        '.mw-body-content',
        '#bodyContent'
    ]
    
    main_content = None
    for selector in content_selectors:
        main_content = soup.select_one(selector)
        if main_content:
            logger.info(f"Found Wikipedia content using: {selector}")
            break
    
    if not main_content:
        logger.info("Using body as fallback for Wikipedia")
        main_content = soup.find('body')
    
    # Remove Wikipedia-specific unwanted elements
    unwanted_selectors = [
        '.mw-jump-link',
        '.mw-editsection',
        '.reference',
        '.references',
        '.navbox',
        '.infobox',
        '.vertical-navbox',
        '.quotebox',
        '.metadata',
        '.ambox',
        '.sistersitebox',
        '.printfooter',
        '#siteSub',
        '#jump-to-nav',
        '.catlinks',
        '#External_links',
        '#References',
        '#Further_reading',
        '#Notes',
        '.navbox',
        '.vertical-navbox',
        '.infobox',
        '.sidebar',
        '.mw-redirect',
        '.external',
        '[role="navigation"]',
        '.mw-headline',
        '.toc',
        '#toc',
        '.hatnote',
        '.shortdescription',
        '.nomobile'
    ]
    
    for selector in unwanted_selectors:
        elements = main_content.select(selector)
        for element in elements:
            element.decompose()
    
    # Also remove edit sections and navigation
    for element in main_content.find_all(['span', 'div']):
        classes = element.get('class', [])
        if classes and any('edit' in str(cls).lower() for cls in classes):
            element.decompose()
    
    logger.info("Cleaned Wikipedia unwanted elements")
    
    # Extract only the meaningful content
    content_elements = []
    seen_texts = set()  # Avoid duplicates
    
    for element in main_content.find_all(['h1', 'h2', 'h3', 'p', 'ul', 'ol', 'li']):
        # Skip empty elements
        text = safe_get_text(element)
        if not text or len(text) < 10:
            continue
        
        # Skip duplicates
        if text in seen_texts:
            continue
        seen_texts.add(text)
        
        # Skip navigation-like text
        if any(nav_word in text.lower() for nav_word in ['jump to', 'navigation', 'menu', 'search']):
            continue
            
        content_elements.append(element)
    
    logger.info(f"Found {len(content_elements)} Wikipedia content elements")
    
    # If we have very few elements, try a broader approach
    if len(content_elements) < 5:
        logger.info("Using broader content extraction for Wikipedia...")
        content_elements = []
        seen_texts = set()
        
        # Get all paragraphs and headings with substantial text
        for element in main_content.find_all(['h1', 'h2', 'h3', 'p']):
            text = safe_get_text(element)
            if text and len(text) > 20 and text not in seen_texts:
                content_elements.append(element)
                seen_texts.add(text)
    
    logger.info(f"Final Wikipedia content elements: {len(content_elements)}")
    
    # Build cleaned HTML
    cleaned_html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{title_text} - Wikipedia</title>
    <style>
        body {{ 
            font-family: 'Georgia', 'Times New Roman', serif; 
            line-height: 1.7; 
            max-width: 800px; 
            margin: 40px auto; 
            padding: 20px; 
            color: #333;
        }}
        h1 {{ 
            font-size: 32px; 
            margin-bottom: 30px; 
            color: #1a1a1a; 
            border-bottom: 3px solid #2c5282; 
            padding-bottom: 15px;
            text-align: center;
        }}
        h2 {{ 
            font-size: 24px; 
            margin-top: 40px; 
            margin-bottom: 20px; 
            color: #2d3748; 
            border-bottom: 1px solid #cbd5e0;
            padding-bottom: 8px;
        }}
        h3 {{ 
            font-size: 20px; 
            margin-top: 30px; 
            margin-bottom: 15px; 
            color: #4a5568; 
        }}
        p {{ 
            margin-bottom: 20px; 
            text-align: justify;
            font-size: 16px;
            line-height: 1.8;
        }}
        ul, ol {{ 
            margin-bottom: 20px; 
            padding-left: 40px; 
        }}
        li {{
            margin-bottom: 10px;
            font-size: 16px;
            line-height: 1.6;
        }}
    </style>
</head>
<body>
    <h1>{title_text}</h1>
"""
    
    # Add content elements
    for element in content_elements:
        cleaned_html += str(element) + '\n'
    
    # Add footer if we have content
    if content_elements:
        cleaned_html += """
    <div style="margin-top: 50px; padding-top: 20px; border-top: 1px solid #e2e8f0; font-size: 14px; color: #718096; text-align: center;">
        Source: Wikipedia - The Free Encyclopedia
    </div>
"""
    else:
        cleaned_html += """
    <div style="text-align: center; color: #666; margin-top: 100px;">
        <h3>No article content could be extracted</h3>
        <p>The page might have a different structure than expected.</p>
    </div>
"""
    
    cleaned_html += "</body></html>"
    
    return cleaned_html, title_text

def parse_general_article(html: str) -> tuple[str, str]:
    """Parser for general websites"""
    soup = BeautifulSoup(html, 'lxml')
    
    # Remove unwanted elements
    unwanted_tags = ['script', 'style', 'nav', 'header', 'footer', 'aside', 'iframe', 'noscript']
    for tag in unwanted_tags:
        for element in soup.find_all(tag):
            element.decompose()
    
    # Remove elements with unwanted classes
    unwanted_classes = ['ad', 'advertisement', 'banner', 'sidebar', 'comment', 'social', 'share', 'menu', 'popup']
    for class_name in unwanted_classes:
        for element in soup.find_all(class_=lambda x: x and class_name in str(x).lower()):
            element.decompose()
    
    # Find title safely
    title_element = soup.find('h1') or soup.find('title')
    title_text = safe_get_text(title_element, "Article")
    
    # Find main content
    content_selectors = [
        'article',
        'main',
        '[role="main"]',
        '.content',
        '.article',
        '.post',
        '.story',
        '.entry-content',
        '.post-content',
        '#content',
        '#main',
        '#article'
    ]
    
    main_content = None
    for selector in content_selectors:
        main_content = soup.select_one(selector)
        if main_content:
            logger.info(f"Found content using selector: {selector}")
            break
    
    if not main_content:
        logger.info("Using body as fallback for general article")
        main_content = soup.find('body')
    
    # Extract content
    content_elements = []
    seen_texts = set()
    
    for element in main_content.find_all(['h1', 'h2', 'h3', 'p', 'ul', 'ol', 'img']):
        if element.name == 'img':
            content_elements.append(element)
        else:
            text = safe_get_text(element)
            if text and len(text) > 10 and text not in seen_texts:
                content_elements.append(element)
                seen_texts.add(text)
    
    logger.info(f"Found {len(content_elements)} general article content elements")
    
    # Build cleaned HTML
    cleaned_html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{title_text}</title>
    <style>
        body {{ 
            font-family: 'Georgia', serif; 
            line-height: 1.6; 
            max-width: 700px; 
            margin: 40px auto; 
            padding: 20px; 
            color: #333;
        }}
        h1 {{ 
            font-size: 28px; 
            margin-bottom: 20px; 
            color: #1a1a1a; 
            border-bottom: 2px solid #4a5568;
            padding-bottom: 10px;
        }}
        h2 {{ 
            font-size: 22px; 
            margin-top: 30px; 
            margin-bottom: 15px; 
            color: #2d3748; 
        }}
        h3 {{ 
            font-size: 18px; 
            margin-top: 25px; 
            margin-bottom: 12px; 
            color: #4a5568; 
        }}
        p {{ 
            margin-bottom: 16px; 
            text-align: justify;
        }}
        img {{ 
            max-width: 100%; 
            height: auto; 
            display: block; 
            margin: 20px auto;
        }}
        ul, ol {{ 
            margin-bottom: 16px; 
            padding-left: 30px; 
        }}
    </style>
</head>
<body>
    <h1>{title_text}</h1>
"""
    
    for element in content_elements:
        if element.name == 'img':
            src = element.get('src', '')
            if src:
                # Handle relative URLs
                if src.startswith('//'):
                    src = f"https:{src}"
                cleaned_html += f'<img src="{src}" alt="{element.get("alt", "")}" />\n'
        else:
            cleaned_html += str(element) + '\n'
    
    cleaned_html += "</body></html>"
    
    return cleaned_html, title_text

def parse_article(html: str, url: str) -> tuple[str, str]:
    """Choose the appropriate parser based on URL"""
    try:
        if 'wikipedia.org' in url:
            return parse_wikipedia(html)
        else:
            return parse_general_article(html)
    except Exception as e:
        logger.error(f"Error in parse_article: {e}")
        # Return a basic HTML as fallback
        fallback_html = """
        <!DOCTYPE html>
        <html>
        <head><title>Article</title></head>
        <body>
            <h1>Article Content</h1>
            <p>Unable to parse the article content properly.</p>
        </body>
        </html>
        """
        return fallback_html, "Article"

def save_debug_files(request_id: str, html: str, cleaned_html: str, title: str):
    """Save debug files to inspect parsing"""
    debug_dir = os.path.join(PDF_OUTPUT_DIR, 'debug')
    os.makedirs(debug_dir, exist_ok=True)
    
    try:
        # Save original HTML
        with open(os.path.join(debug_dir, f'{request_id}_original.html'), 'w', encoding='utf-8') as f:
            f.write(html)
        
        # Save cleaned HTML
        with open(os.path.join(debug_dir, f'{request_id}_cleaned.html'), 'w', encoding='utf-8') as f:
            f.write(cleaned_html)
        
        # Save extracted text only
        soup = BeautifulSoup(cleaned_html, 'lxml')
        text_only = soup.get_text(separator='\n', strip=True)
        with open(os.path.join(debug_dir, f'{request_id}_text.txt'), 'w', encoding='utf-8') as f:
            f.write(f"TITLE: {title}\n")
            f.write("=" * 80 + "\n\n")
            f.write(text_only)
        
        # Save parsing stats
        elements = soup.find_all(['h1', 'h2', 'h3', 'p', 'ul', 'ol'])
        with open(os.path.join(debug_dir, f'{request_id}_stats.txt'), 'w', encoding='utf-8') as f:
            f.write(f"Request ID: {request_id}\n")
            f.write(f"Title: {title}\n")
            f.write(f"Original HTML length: {len(html):,} characters\n")
            f.write(f"Cleaned HTML length: {len(cleaned_html):,} characters\n")
            f.write(f"Text length: {len(text_only):,} characters\n")
            f.write(f"Total elements: {len(elements)}\n")
            f.write(f"\nElement breakdown:\n")
            counts = Counter([e.name for e in elements])
            for tag, count in counts.items():
                f.write(f"  {tag}: {count}\n")
        
        logger.info(f"Debug files saved for request {request_id}")
        
    except Exception as e:
        logger.error(f"Error saving debug files: {e}")

async def generate_pdf_playwright(html_content: str, output_path: str):
    """Generate PDF from HTML content using Playwright"""
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                args=[
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-gpu'
                ]
            )
            page = await browser.new_page()
            
            await page.set_content(html_content, wait_until='networkidle')
            await page.wait_for_timeout(2000)  # Wait for resources
            
            await page.pdf(
                path=output_path,
                format='A4',
                margin={'top': '20mm', 'right': '20mm', 'bottom': '20mm', 'left': '20mm'},
                print_background=True,
                display_header_footer=False
            )
            
            await browser.close()
            logger.info(f"PDF generated successfully: {output_path}")
            
    except Exception as e:
        logger.error(f"Error generating PDF: {e}")
        raise HTTPException(status_code=500, detail=f"PDF generation failed: {str(e)}")

async def notify_backend(request_id: str, pdf_path: str = None, status: str = "completed", error: str = None):
    """Notify backend service about PDF generation status"""
    try:
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)) as session:
            payload = {
                "requestId": request_id,
                "pdfPath": pdf_path,
                "status": status,
                "error": error,
                "timestamp": datetime.now().isoformat()
            }
            
            async with session.post(f"{BACKEND_URL}/api/update-pdf", json=payload) as response:
                if response.status == 200:
                    logger.info(f"Successfully notified backend for request {request_id}")
                else:
                    logger.warning(f"Backend notification returned status {response.status}")
                    
    except Exception as e:
        logger.error(f"Error notifying backend: {e}")

@app.post("/generate-pdf", response_model=PDFResponse)
async def generate_pdf(request: PDFRequest, background_tasks: BackgroundTasks):
    """Endpoint to trigger PDF generation"""
    logger.info(f"Received PDF request {request.requestId} for URL: {request.url}")
    
    # Validate request ID
    if not request.requestId or len(request.requestId) > 100:
        raise HTTPException(status_code=400, detail="Invalid request ID")
    
    # Start background task
    background_tasks.add_task(process_pdf_generation, request.requestId, str(request.url))
    
    return PDFResponse(
        status="processing",
        requestId=request.requestId,
        message="PDF generation started"
    )

async def process_pdf_generation(request_id: str, url: str):
    """Background task to process PDF generation"""
    try:
        logger.info(f"Starting PDF generation for {request_id}")
        
        # Fetch HTML
        html = await fetch_html(url)
        
        # Parse and clean article with URL-specific parser
        cleaned_html, title = parse_article(html, url)
        
        # Save debug files
        save_debug_files(request_id, html, cleaned_html, title)
        
        # Generate PDF
        pdf_filename = f"{request_id}.pdf"
        pdf_path = os.path.join(PDF_OUTPUT_DIR, pdf_filename)
        await generate_pdf_playwright(cleaned_html, pdf_path)
        
        # Notify backend
        await notify_backend(request_id, pdf_path, "completed")
        logger.info(f"PDF generation completed for {request_id}")
        
    except HTTPException:
        # Re-raise HTTP exceptions to preserve status codes
        raise
    except Exception as e:
        logger.error(f"Error processing PDF generation for {request_id}: {e}")
        await notify_backend(request_id, None, "failed", str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "PDF Generator",
        "timestamp": datetime.now().isoformat(),
        "pdf_output_dir": PDF_OUTPUT_DIR
    }

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Article PDF Generator Service",
        "version": "1.0.0",
        "endpoints": {
            "generate_pdf": "POST /generate-pdf",
            "health": "GET /health"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )