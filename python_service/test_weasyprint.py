"""
Quick test to verify WeasyPrint PDF generation works
"""
from weasyprint import HTML
import os

def test_simple_pdf():
    """Test basic PDF generation"""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Test PDF</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                padding: 40px;
                line-height: 1.6;
            }
            h1 {
                color: #2c5282;
                border-bottom: 2px solid #2c5282;
                padding-bottom: 10px;
            }
            p {
                margin: 20px 0;
            }
        </style>
    </head>
    <body>
        <h1>WeasyPrint Test</h1>
        <p>This is a test PDF generated using WeasyPrint.</p>
        <p>It supports CSS styling and modern HTML.</p>
        <h2>Benefits</h2>
        <ul>
            <li>No browser dependencies</li>
            <li>Excellent CSS support</li>
            <li>Works in CI/CD environments</li>
            <li>Pure Python solution</li>
        </ul>
    </body>
    </html>
    """
    
    output_path = "test_output.pdf"
    
    try:
        HTML(string=html_content).write_pdf(output_path)
        
        if os.path.exists(output_path):
            file_size = os.path.getsize(output_path)
            print(f"✅ PDF generated successfully!")
            print(f"📄 File: {output_path}")
            print(f"📊 Size: {file_size:,} bytes")
            return True
        else:
            print("❌ PDF file was not created")
            return False
            
    except Exception as e:
        print(f"❌ Error generating PDF: {e}")
        return False
    finally:
        # Cleanup
        if os.path.exists(output_path):
            os.remove(output_path)

if __name__ == "__main__":
    print("Testing WeasyPrint PDF generation...\n")
    success = test_simple_pdf()
    exit(0 if success else 1)
