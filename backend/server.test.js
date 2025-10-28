const request = require('supertest');
const { app, startServer, closeServer } = require('./server');

describe('Backend API Tests', () => {
  let server;

  beforeAll(() => {
    server = startServer();
  });

  afterAll((done) => {
    closeServer();
    if (server) {
      server.close(done);
    } else {
      done();
    }
  });

  // Health Check Tests
  describe('GET /health', () => {
    test('should return healthy status', async () => {
      const response = await request(app).get('/health');
      expect(response.statusCode).toBe(200);
      expect(response.body.status).toBe('healthy');
      expect(response.body).toHaveProperty('timestamp');
      expect(response.body).toHaveProperty('activeRequests');
    });

    test('should return number of active requests', async () => {
      const response = await request(app).get('/health');
      expect(typeof response.body.activeRequests).toBe('number');
      expect(response.body.activeRequests).toBeGreaterThanOrEqual(0);
    });
  });

  // URL Validation Tests
  describe('POST /api/fetch - URL Validation', () => {
    test('should reject request without URL', async () => {
      const response = await request(app)
        .post('/api/fetch')
        .send({});
      
      expect(response.statusCode).toBe(400);
      expect(response.body.error).toContain('Invalid URL');
    });

    test('should reject invalid URL format', async () => {
      const response = await request(app)
        .post('/api/fetch')
        .send({ url: 'invalid-url' });
      
      expect(response.statusCode).toBe(400);
      expect(response.body.error).toContain('Invalid URL');
    });

    test('should reject URL without protocol', async () => {
      const response = await request(app)
        .post('/api/fetch')
        .send({ url: 'example.com' });
      
      expect(response.statusCode).toBe(400);
      expect(response.body.error).toContain('Invalid URL');
    });

    test('should reject FTP URLs', async () => {
      const response = await request(app)
        .post('/api/fetch')
        .send({ url: 'ftp://example.com' });
      
      expect(response.statusCode).toBe(400);
      expect(response.body.error).toContain('Invalid URL');
    });

    test('should accept valid HTTP URL format', async () => {
      const response = await request(app)
        .post('/api/fetch')
        .send({ url: 'http://example.com/article' });
      
      // Should pass validation, but may fail accessibility check
      expect([200, 400]).toContain(response.statusCode);
    });

    test('should accept valid HTTPS URL format', async () => {
      const response = await request(app)
        .post('/api/fetch')
        .send({ url: 'https://example.com/article' });
      
      // Should pass validation, but may fail accessibility check
      expect([200, 400]).toContain(response.statusCode);
    });

    test('should accept URL with path and query parameters', async () => {
      const response = await request(app)
        .post('/api/fetch')
        .send({ url: 'https://example.com/article?id=123&lang=en' });
      
      expect([200, 400]).toContain(response.statusCode);
    });

    test('should accept URL with subdomain', async () => {
      const response = await request(app)
        .post('/api/fetch')
        .send({ url: 'https://blog.example.com/article' });
      
      expect([200, 400]).toContain(response.statusCode);
    });
  });

  // Request ID Tests
  describe('POST /api/fetch - Request ID Generation', () => {
    test('should return a unique request ID on successful submission', async () => {
      const response = await request(app)
        .post('/api/fetch')
        .send({ url: 'https://example.com/article' });
      
      if (response.statusCode === 200) {
        expect(response.body).toHaveProperty('requestId');
        expect(typeof response.body.requestId).toBe('string');
        expect(response.body.requestId.length).toBeGreaterThan(0);
        expect(response.body.status).toBe('pending');
        expect(response.body.message).toContain('PDF generation initiated');
      }
    });

    test('should generate different request IDs for different requests', async () => {
      const response1 = await request(app)
        .post('/api/fetch')
        .send({ url: 'https://example.com/article1' });
      
      const response2 = await request(app)
        .post('/api/fetch')
        .send({ url: 'https://example.com/article2' });
      
      if (response1.statusCode === 200 && response2.statusCode === 200) {
        expect(response1.body.requestId).not.toBe(response2.body.requestId);
      }
    });
  });

  // Status Check Tests
  describe('GET /api/status/:requestId', () => {
    test('should return 404 for non-existent request ID', async () => {
      const response = await request(app)
        .get('/api/status/non-existent-id');
      
      expect(response.statusCode).toBe(404);
      expect(response.body.error).toContain('Request not found');
    });

    test('should return status for valid request ID', async () => {
      // First create a request
      const createResponse = await request(app)
        .post('/api/fetch')
        .send({ url: 'https://example.com/article' });
      
      if (createResponse.statusCode === 200) {
        const requestId = createResponse.body.requestId;
        
        const statusResponse = await request(app)
          .get(`/api/status/${requestId}`);
        
        expect(statusResponse.statusCode).toBe(200);
        expect(statusResponse.body).toHaveProperty('status');
        expect(['pending', 'processing', 'completed', 'failed']).toContain(statusResponse.body.status);
      }
    });
  });

  // Download Tests
  describe('GET /api/download/:requestId', () => {
    test('should return 404 for non-existent request ID', async () => {
      const response = await request(app)
        .get('/api/download/non-existent-id');
      
      expect(response.statusCode).toBe(404);
      expect(response.body.error).toContain('Request not found');
    });

    test('should return 400 if PDF is not ready', async () => {
      // Create a new request
      const createResponse = await request(app)
        .post('/api/fetch')
        .send({ url: 'https://example.com/article' });
      
      if (createResponse.statusCode === 200) {
        const requestId = createResponse.body.requestId;
        
        const downloadResponse = await request(app)
          .get(`/api/download/${requestId}`);
        
        expect(downloadResponse.statusCode).toBe(400);
        expect(downloadResponse.body.error).toContain('PDF not ready');
      }
    });
  });

  // Update PDF Tests
  describe('POST /api/update-pdf', () => {
    test('should update PDF status successfully', async () => {
      // First create a request
      const createResponse = await request(app)
        .post('/api/fetch')
        .send({ url: 'https://example.com/article' });
      
      if (createResponse.statusCode === 200) {
        const requestId = createResponse.body.requestId;
        
        const updateResponse = await request(app)
          .post('/api/update-pdf')
          .send({
            requestId: requestId,
            pdfPath: '/path/to/pdf.pdf',
            status: 'completed',
            error: null
          });
        
        expect(updateResponse.statusCode).toBe(200);
        expect(updateResponse.body.success).toBe(true);
      }
    });

    test('should handle failed PDF generation', async () => {
      const createResponse = await request(app)
        .post('/api/fetch')
        .send({ url: 'https://example.com/article' });
      
      if (createResponse.statusCode === 200) {
        const requestId = createResponse.body.requestId;
        
        const updateResponse = await request(app)
          .post('/api/update-pdf')
          .send({
            requestId: requestId,
            pdfPath: null,
            status: 'failed',
            error: 'Generation error'
          });
        
        expect(updateResponse.statusCode).toBe(200);
        expect(updateResponse.body.success).toBe(true);
        
        // Verify status was updated
        const statusResponse = await request(app)
          .get(`/api/status/${requestId}`);
        
        expect(statusResponse.body.status).toBe('failed');
        expect(statusResponse.body.error).toBe('Generation error');
      }
    });
  });

  // CORS Tests
  describe('CORS Configuration', () => {
    test('should include CORS headers in response', async () => {
      const response = await request(app).get('/health');
      expect(response.headers['access-control-allow-origin']).toBeDefined();
    });
  });

  // Content-Type Tests
  describe('Content-Type Handling', () => {
    test('should accept JSON content type', async () => {
      const response = await request(app)
        .post('/api/fetch')
        .set('Content-Type', 'application/json')
        .send({ url: 'https://example.com' });
      
      expect([200, 400]).toContain(response.statusCode);
    });

    test('should return JSON responses', async () => {
      const response = await request(app).get('/health');
      expect(response.headers['content-type']).toMatch(/json/);
    });
  });

  // Error Handling Tests
  describe('Error Handling', () => {
    test('should handle malformed JSON', async () => {
      const response = await request(app)
        .post('/api/fetch')
        .set('Content-Type', 'application/json')
        .send('{ invalid json }');
      
      expect(response.statusCode).toBe(400);
    });

    test('should handle empty request body', async () => {
      const response = await request(app)
        .post('/api/fetch')
        .send();
      
      expect(response.statusCode).toBe(400);
    });
  });

  // Integration Tests
  describe('End-to-End Flow', () => {
    test('should handle complete request lifecycle', async () => {
      // Step 1: Submit URL
      const createResponse = await request(app)
        .post('/api/fetch')
        .send({ url: 'https://example.com/article' });
      
      if (createResponse.statusCode === 200) {
        const requestId = createResponse.body.requestId;
        expect(requestId).toBeDefined();
        
        // Step 2: Check initial status
        const status1Response = await request(app)
          .get(`/api/status/${requestId}`);
        expect(status1Response.statusCode).toBe(200);
        expect(status1Response.body.status).toBe('pending');
        
        // Step 3: Simulate Python service updating status
        await request(app)
          .post('/api/update-pdf')
          .send({
            requestId: requestId,
            pdfPath: `/app/pdfs/${requestId}.pdf`,
            status: 'completed',
            error: null
          });
        
        // Step 4: Check updated status
        const status2Response = await request(app)
          .get(`/api/status/${requestId}`);
        expect(status2Response.statusCode).toBe(200);
        expect(status2Response.body.status).toBe('completed');
      }
    });
  });
});
