
const express = require('express');
const cors = require('cors');
const axios = require('axios');
const { v4: uuidv4 } = require('uuid');
const morgan = require('morgan');
const path = require('path');
const fs = require('fs');
require('dotenv').config();

const app = express();
const PORT = process.env.PORT || 5000;

app.use(cors());
app.use(express.json());
app.use(morgan('combined'));

// In-memory storage (replaces PostgreSQL)
const requests = new Map();

// Create PDFs directory if it doesn't exist
const PDF_DIR = path.join(__dirname, 'pdfs');
if (!fs.existsSync(PDF_DIR)) {
  fs.mkdirSync(PDF_DIR, { recursive: true });
}

const isValidUrl = (url) => {
  const urlPattern = /^https?:\/\/(www\.)?[-a-zA-Z0-9@:%._+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_+.~#?&//=]*)$/;
  return urlPattern.test(url);
};

const checkUrlAccessibility = async (url) => {
  try {
    const response = await axios.head(url, { timeout: 10000, maxRedirects: 5 });
    return response.status >= 200 && response.status < 400;
  } catch (error) {
    if (error.response) {
      return error.response.status >= 200 && error.response.status < 400;
    }
    return false;
  }
};

app.post('/api/fetch', async (req, res) => {
  const { url } = req.body;

  if (!url || !isValidUrl(url)) {
    return res.status(400).json({ error: 'Invalid URL format. Please provide a valid HTTP/HTTPS URL.' });
  }

  const isAccessible = await checkUrlAccessibility(url);
  if (!isAccessible) {
    return res.status(400).json({ error: 'URL is not accessible. Please check the URL and try again.' });
  }

  const requestId = uuidv4();

  // Store in memory instead of database
  requests.set(requestId, {
    id: requestId,
    url: url,
    status: 'pending',
    error_message: null,
    pdf_path: null,
    created_at: new Date().toISOString()
  });

  try {
    // Call Python service to generate PDF
    axios.post(`http://localhost:8000/generate-pdf`, { requestId, url }).catch(err => {
      console.error('Error calling Python service:', err.message);
      const request = requests.get(requestId);
      if (request) {
        request.status = 'failed';
        request.error_message = err.message;
      }
    });

    res.json({ requestId, message: 'PDF generation initiated', status: 'pending' });
  } catch (err) {
    console.error('Error storing request:', err);
    res.status(500).json({ error: 'Failed to process request' });
  }
});

app.get('/api/status/:requestId', async (req, res) => {
  const { requestId } = req.params;
  
  const request = requests.get(requestId);
  
  if (!request) {
    return res.status(404).json({ error: 'Request not found' });
  }

  res.json({ 
    status: request.status, 
    error: request.error_message 
  });
});

app.get('/api/download/:requestId', async (req, res) => {
  const { requestId } = req.params;
  
  const request = requests.get(requestId);
  
  if (!request) {
    return res.status(404).json({ error: 'Request not found' });
  }

  if (request.status !== 'completed') {
    return res.status(400).json({ error: 'PDF not ready yet' });
  }

  if (!request.pdf_path || !fs.existsSync(request.pdf_path)) {
    return res.status(404).json({ error: 'PDF file not found' });
  }

  res.download(request.pdf_path, 'blog.pdf', (err) => {
    if (err) {
      console.error('Download error:', err);
      res.status(500).json({ error: 'Failed to download PDF' });
    }
  });
});

app.post('/api/update-pdf', async (req, res) => {
  const { requestId, pdfPath, status, error } = req.body;
  
  const request = requests.get(requestId);
  
  if (request) {
    request.status = status;
    request.pdf_path = pdfPath;
    request.error_message = error;
    request.updated_at = new Date().toISOString();
  }

  res.json({ success: true });
});

app.get('/health', (req, res) => {
  res.json({ 
    status: 'healthy', 
    timestamp: new Date().toISOString(),
    activeRequests: requests.size
  });
});

let server;

const startServer = () => {
  server = app.listen(PORT, '0.0.0.0', () => {
    console.log(`Backend server running on port ${PORT}`);
    console.log('Using in-memory storage (no database)');
  });
  return server;
};

const closeServer = () => {
  if (server) {
    server.close();
  }
};

if (require.main === module) {
  startServer();
}

module.exports = { app, startServer, closeServer };
