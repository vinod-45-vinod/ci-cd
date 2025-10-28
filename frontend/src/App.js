import React, { useState } from 'react';
import './App.css';

function App() {
  const [url, setUrl] = useState('');
  const [status, setStatus] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [downloadUrl, setDownloadUrl] = useState('');

  // SKYB-3: URL validation regex
  const validateUrl = (input) => {
    const urlPattern = /^https?:\/\/(www\.)?[-a-zA-Z0-9@:%._+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_+.~#?&//=]*)$/;
    return urlPattern.test(input);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setDownloadUrl('');
    setStatus('');

    // SKYB-3: Frontend validation
    if (!validateUrl(url)) {
      setError('Please enter a valid URL (must start with http:// or https://)');
      return;
    }

    setLoading(true);
    setStatus('Validating URL...');

    try {
      // SKYB-2: Submit URL to backend
      const response = await fetch('/api/fetch', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ url }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || 'Failed to generate PDF');
      }

      setStatus('Fetching article content...');

      // Poll for PDF generation status
      const requestId = data.requestId;
      await pollForPdf(requestId);

    } catch (err) {
      setError(err.message);
      setLoading(false);
      setStatus('');
    }
  };

  const pollForPdf = async (requestId) => {
    const maxAttempts = 30;
    let attempts = 0;

    const poll = async () => {
      try {
        const response = await fetch(`/api/status/${requestId}`);
        const data = await response.json();

        if (data.status === 'completed') {
          setStatus('PDF generated successfully!');
          setDownloadUrl(`/api/download/${requestId}`);
          setLoading(false);
          return;
        } else if (data.status === 'failed') {
          throw new Error(data.error || 'PDF generation failed');
        } else if (data.status === 'processing') {
          setStatus('Generating PDF...');
        }

        attempts++;
        if (attempts < maxAttempts) {
          setTimeout(poll, 2000);
        } else {
          throw new Error('PDF generation timed out');
        }
      } catch (err) {
        setError(err.message);
        setLoading(false);
        setStatus('');
      }
    };

    poll();
  };

  // SKYB-17: Handle download with blob
  const handleDownload = async () => {
    try {
      const response = await fetch(downloadUrl);
      const blob = await response.blob();
      const fileUrl = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = fileUrl;
      link.setAttribute('download', 'article.pdf');
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(fileUrl);
    } catch (err) {
      setError('Failed to download PDF');
    }
  };

  return (
    <div className="App">
      <div className="container">
        <header className="header">
          <h1>Article to PDF Converter</h1>
          <p>Convert any web article into a clean, downloadable PDF</p>
        </header>

        <main className="main-content">
          <form onSubmit={handleSubmit} className="url-form">
            <div className="input-group">
              <input
                type="text"
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                placeholder="Enter article URL (e.g., https://example.com/article)"
                className="url-input"
                disabled={loading}
              />
              <button 
                type="submit" 
                className="submit-btn"
                disabled={loading}
              >
                {loading ? 'Processing...' : 'Generate PDF'}
              </button>
            </div>
          </form>

          {error && (
            <div className="message error-message">
              <span className="icon">⚠️</span>
              {error}
            </div>
          )}

          {status && (
            <div className="message status-message">
              <span className="icon">🔄</span>
              {status}
            </div>
          )}

          {downloadUrl && (
            <div className="download-section">
              <div className="message success-message">
                <span className="icon">✓</span>
                Your PDF is ready!
              </div>
              <button onClick={handleDownload} className="download-btn">
                Download PDF
              </button>
            </div>
          )}
        </main>

        <footer className="footer">
          <p>Sprint 1 Demo • SKYB-2 to SKYB-17</p>
        </footer>
      </div>
    </div>
  );
}

export default App;