const request = require('supertest');
const { app, startServer } = require('./server');

describe('Backend API Tests', () => {
  let server;

  beforeAll(() => {
    server = startServer();
  });

  afterAll((done) => {
    if (server) {
      server.close((err) => {
        if (err) console.error('Error closing server:', err);
        done();
      });
    } else {
      done();
    }
  });

  test('should accept Wikipedia India URL for blog submission', async () => {
    const testUrl = 'https://en.wikipedia.org/wiki/India';
    const response = await request(app)
      .post('/api/fetch')
      .send({ url: testUrl });
    
    expect(response.status).toBe(200);
    expect(response.body).toHaveProperty('requestId');
  });
});
