module.exports = {
  testEnvironment: 'node',
  collectCoverageFrom: [
    '**/*.js',
    '!node_modules/**',
    '!coverage/**',
    '!jest.config.js',
  ],
  coverageThreshold: {
    global: {
      branches: 52,
      functions: 73,
      lines: 73,
      statements: 73,
    },
  },
  coverageReporters: ['html', 'text', 'lcov', 'json-summary'],
  testMatch: ['**/*.test.js'],
  testTimeout: 10000,
};
