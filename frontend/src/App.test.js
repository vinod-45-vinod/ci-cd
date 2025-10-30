import { render, screen, fireEvent } from '@testing-library/react';
import App from './App';

describe('App Component', () => {
  beforeEach(() => {
    global.fetch = jest.fn();
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  test('should accept Wikipedia India URL input', () => {
    render(<App />);
    
    const testUrl = 'https://en.wikipedia.org/wiki/India';
    const input = screen.getByPlaceholderText(/Enter blog URL/i);
    
    fireEvent.change(input, { target: { value: testUrl } });
    
    expect(input.value).toBe(testUrl);
  });
});
