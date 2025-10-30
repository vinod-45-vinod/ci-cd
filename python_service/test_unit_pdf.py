from main import parse_general_article


def test_parse_general_article_basic():
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
