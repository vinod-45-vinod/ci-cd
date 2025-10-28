import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import App from './App';

describe('App Component', () => {
  beforeEach(() => {
    // Reset fetch mock before each test
    global.fetch = jest.fn();
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  test('renders article to pdf converter heading', () => {
    render(<App />);
    const headingElement = screen.getByText(/Article to PDF Converter/i);
    expect(headingElement).toBeInTheDocument();
  });

  test('renders input field and button', () => {
    render(<App />);
    const input = screen.getByPlaceholderText(/Enter article URL/i);
    const button = screen.getByRole('button', { name: /Generate PDF/i });
    
    expect(input).toBeInTheDocument();
    expect(button).toBeInTheDocument();
  });

  test('shows error for invalid URL', () => {
    render(<App />);
    const input = screen.getByPlaceholderText(/Enter article URL/i);
    const button = screen.getByText(/Generate PDF/i);

    fireEvent.change(input, { target: { value: 'invalid-url' } });
    fireEvent.click(button);

    const errorMessage = screen.getByText(/Please enter a valid URL/i);
    expect(errorMessage).toBeInTheDocument();
  });

  test('accepts valid URL format', () => {
    render(<App />);
    const input = screen.getByPlaceholderText(/Enter article URL/i);

    fireEvent.change(input, { target: { value: 'https://example.com/article' } });
    expect(input.value).toBe('https://example.com/article');
  });

  test('shows validation error for URL without protocol', async () => {
    render(<App />);
    const input = screen.getByPlaceholderText(/Enter article URL/i);
    const button = screen.getByRole('button', { name: /Generate PDF/i });

    await userEvent.type(input, 'example.com');
    fireEvent.click(button);

    await waitFor(() => {
      expect(screen.getByText(/Please enter a valid URL/i)).toBeInTheDocument();
    });
  });

  test('submits valid URL and shows processing status', async () => {
    global.fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ requestId: 'test-123', status: 'pending' }),
    });

    render(<App />);
    const input = screen.getByPlaceholderText(/Enter article URL/i);
    const button = screen.getByRole('button', { name: /Generate PDF/i });

    await userEvent.type(input, 'https://example.com/article');
    fireEvent.click(button);

    await waitFor(() => {
      expect(screen.getByText(/Validating URL/i)).toBeInTheDocument();
    });

    expect(global.fetch).toHaveBeenCalledWith('/api/fetch', expect.any(Object));
  });

  test('handles server error response', async () => {
    global.fetch.mockResolvedValueOnce({
      ok: false,
      json: async () => ({ error: 'Server error occurred' }),
    });

    render(<App />);
    const input = screen.getByPlaceholderText(/Enter article URL/i);
    const button = screen.getByRole('button', { name: /Generate PDF/i });

    await userEvent.type(input, 'https://example.com/article');
    fireEvent.click(button);

    await waitFor(() => {
      expect(screen.getByText(/Server error occurred/i)).toBeInTheDocument();
    });
  });

  test('polls for PDF status and shows completion', async () => {
    // Mock initial fetch request
    global.fetch
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ requestId: 'test-123', status: 'pending' }),
      })
      // Mock status check - processing
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ status: 'processing' }),
      })
      // Mock status check - completed
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ status: 'completed' }),
      });

    render(<App />);
    const input = screen.getByPlaceholderText(/Enter article URL/i);
    const button = screen.getByRole('button', { name: /Generate PDF/i });

    await userEvent.type(input, 'https://example.com/article');
    fireEvent.click(button);

    await waitFor(() => {
      expect(screen.getByText(/Generating PDF/i)).toBeInTheDocument();
    }, { timeout: 3000 });

    await waitFor(() => {
      expect(screen.getByText(/PDF generated successfully/i)).toBeInTheDocument();
    }, { timeout: 5000 });

    expect(screen.getByRole('button', { name: /Download PDF/i })).toBeInTheDocument();
  });

  test('handles PDF generation failure', async () => {
    global.fetch
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ requestId: 'test-123', status: 'pending' }),
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ status: 'failed', error: 'Generation failed' }),
      });

    render(<App />);
    const input = screen.getByPlaceholderText(/Enter article URL/i);
    const button = screen.getByRole('button', { name: /Generate PDF/i });

    await userEvent.type(input, 'https://example.com/article');
    fireEvent.click(button);

    await waitFor(() => {
      expect(screen.getByText(/Generation failed/i)).toBeInTheDocument();
    }, { timeout: 5000 });
  });

  test('handles download button click', async () => {
    // Mock window.URL.createObjectURL
    global.URL.createObjectURL = jest.fn(() => 'blob:mock-url');
    global.URL.revokeObjectURL = jest.fn();

    // Mock successful PDF generation
    global.fetch
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ requestId: 'test-123', status: 'pending' }),
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ status: 'completed' }),
      })
      .mockResolvedValueOnce({
        ok: true,
        blob: async () => new Blob(['pdf content'], { type: 'application/pdf' }),
      });

    render(<App />);
    const input = screen.getByPlaceholderText(/Enter article URL/i);
    const submitButton = screen.getByRole('button', { name: /Generate PDF/i });

    await userEvent.type(input, 'https://example.com/article');
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(screen.getByText(/PDF generated successfully/i)).toBeInTheDocument();
    }, { timeout: 5000 });

    const downloadButton = screen.getByRole('button', { name: /Download PDF/i });
    fireEvent.click(downloadButton);

    await waitFor(() => {
      expect(global.URL.createObjectURL).toHaveBeenCalled();
    });
  });

  test('disables input and button during processing', async () => {
    global.fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ requestId: 'test-123', status: 'pending' }),
    });

    render(<App />);
    const input = screen.getByPlaceholderText(/Enter article URL/i);
    const button = screen.getByRole('button', { name: /Generate PDF/i });

    await userEvent.type(input, 'https://example.com/article');
    fireEvent.click(button);

    await waitFor(() => {
      expect(input).toBeDisabled();
      expect(screen.getByRole('button', { name: /Processing/i })).toBeDisabled();
    });
  });

  test('renders footer with sprint information', () => {
    render(<App />);
    expect(screen.getByText(/Sprint 1 Demo/i)).toBeInTheDocument();
  });

  test('handles network error during fetch', async () => {
    global.fetch.mockRejectedValueOnce(new Error('Network error'));

    render(<App />);
    const input = screen.getByPlaceholderText(/Enter article URL/i);
    const button = screen.getByRole('button', { name: /Generate PDF/i });

    await userEvent.type(input, 'https://example.com/article');
    fireEvent.click(button);

    await waitFor(() => {
      expect(screen.getByText(/Network error/i)).toBeInTheDocument();
    });
  });

  test('clears previous errors on new submission', async () => {
    render(<App />);
    const input = screen.getByPlaceholderText(/Enter article URL/i);
    const button = screen.getByRole('button', { name: /Generate PDF/i });

    // First submission with invalid URL
    fireEvent.change(input, { target: { value: 'invalid' } });
    fireEvent.click(button);

    await waitFor(() => {
      expect(screen.getByText(/Please enter a valid URL/i)).toBeInTheDocument();
    });

    // Try again with valid URL
    fireEvent.change(input, { target: { value: 'https://example.com' } });
    
    global.fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ requestId: 'test-123', status: 'pending' }),
    });

    fireEvent.click(button);

    await waitFor(() => {
      expect(screen.queryByText(/Please enter a valid URL/i)).not.toBeInTheDocument();
    });
  });
});
