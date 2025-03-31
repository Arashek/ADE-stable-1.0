import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import { AIPairProgramming } from '../AIPairProgramming';
import { CollaborationService } from '../../../services/collaboration/CollaborationService';
import { AICodeAnalysisService } from '../../../services/ai/AICodeAnalysisService';

// Mock the services
jest.mock('../../../services/collaboration/CollaborationService');
jest.mock('../../../services/ai/AICodeAnalysisService');

const mockSuggestion = {
  id: '1',
  type: 'code' as const,
  message: 'Consider using async/await here',
  code: 'async function example() {\n  await fetch("/api");\n}',
  explanation: 'Using async/await makes the code more readable',
  confidence: 0.85,
  timestamp: Date.now(),
};

const mockTextChange = {
  file: 'test.ts',
  from: { line: 1, column: 1 },
  to: { line: 1, column: 10 },
  text: 'const x = 5;',
  origin: 'input',
};

const theme = createTheme();

describe('AIPairProgramming', () => {
  let mockSubscribe: jest.Mock;
  let mockGenerateSuggestion: jest.Mock;

  beforeEach(() => {
    mockSubscribe = jest.fn();
    mockGenerateSuggestion = jest.fn();

    (CollaborationService.getInstance as jest.Mock).mockReturnValue({
      onTextChange: () => ({
        subscribe: mockSubscribe,
      }),
    });

    (AICodeAnalysisService.getInstance as jest.Mock).mockReturnValue({
      generateSuggestion: mockGenerateSuggestion,
    });

    global.fetch = jest.fn().mockImplementation(() =>
      Promise.resolve({
        ok: true,
        json: () => Promise.resolve([mockSuggestion]),
      })
    );
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  it('renders the AI Assistant title', () => {
    render(
      <ThemeProvider theme={theme}>
        <AIPairProgramming sessionId="test-session" currentFile="test.ts" />
      </ThemeProvider>
    );

    expect(screen.getByText('AI Assistant')).toBeInTheDocument();
  });

  it('subscribes to text changes on mount', () => {
    render(
      <ThemeProvider theme={theme}>
        <AIPairProgramming sessionId="test-session" currentFile="test.ts" />
      </ThemeProvider>
    );

    expect(mockSubscribe).toHaveBeenCalled();
  });

  it('displays suggestions when received', async () => {
    mockSubscribe.mockImplementation((callback) => {
      callback(mockTextChange);
      return { unsubscribe: jest.fn() };
    });

    render(
      <ThemeProvider theme={theme}>
        <AIPairProgramming sessionId="test-session" currentFile="test.ts" />
      </ThemeProvider>
    );

    await waitFor(() => {
      expect(screen.getByText(mockSuggestion.message)).toBeInTheDocument();
    });
  });

  it('allows expanding and collapsing suggestions', async () => {
    mockSubscribe.mockImplementation((callback) => {
      callback(mockTextChange);
      return { unsubscribe: jest.fn() };
    });

    render(
      <ThemeProvider theme={theme}>
        <AIPairProgramming sessionId="test-session" currentFile="test.ts" />
      </ThemeProvider>
    );

    await waitFor(() => {
      expect(screen.getByText(mockSuggestion.message)).toBeInTheDocument();
    });

    // Click to expand
    fireEvent.click(screen.getByText(mockSuggestion.message));

    await waitFor(() => {
      expect(screen.getByText(mockSuggestion.explanation!)).toBeInTheDocument();
    });

    await waitFor(() => {
      expect(screen.getByText(mockSuggestion.code!)).toBeInTheDocument();
    });

    // Click to collapse
    fireEvent.click(screen.getByText(mockSuggestion.message));

    await waitFor(() => {
      expect(screen.queryByText(mockSuggestion.explanation!)).not.toBeVisible();
    });
  });

  it('handles submitting queries', async () => {
    const mockQueryResponse = {
      ...mockSuggestion,
      id: '2',
      message: 'Query response',
    };

    global.fetch = jest.fn().mockImplementation(() =>
      Promise.resolve({
        ok: true,
        json: () => Promise.resolve(mockQueryResponse),
      })
    );

    render(
      <ThemeProvider theme={theme}>
        <AIPairProgramming sessionId="test-session" currentFile="test.ts" />
      </ThemeProvider>
    );

    const input = screen.getByPlaceholderText('Ask the AI assistant...');
    fireEvent.change(input, { target: { value: 'How do I use async/await?' } });
    fireEvent.submit(input);

    await waitFor(() => {
      expect(screen.getByText('Query response')).toBeInTheDocument();
    });
  });

  it('handles feedback submission', async () => {
    mockSubscribe.mockImplementation((callback) => {
      callback(mockTextChange);
      return { unsubscribe: jest.fn() };
    });

    render(
      <ThemeProvider theme={theme}>
        <AIPairProgramming sessionId="test-session" currentFile="test.ts" />
      </ThemeProvider>
    );

    await waitFor(() => {
      expect(screen.getByText(mockSuggestion.message)).toBeInTheDocument();
    });

    // Expand suggestion
    fireEvent.click(screen.getByText(mockSuggestion.message));

    // Click thumbs up
    const thumbsUp = screen.getByTitle('Helpful');
    fireEvent.click(thumbsUp);

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith('/api/ai/feedback', expect.any(Object));
    });
  });

  it('displays confidence level correctly', async () => {
    mockSubscribe.mockImplementation((callback) => {
      callback(mockTextChange);
      return { unsubscribe: jest.fn() };
    });

    render(
      <ThemeProvider theme={theme}>
        <AIPairProgramming sessionId="test-session" currentFile="test.ts" />
      </ThemeProvider>
    );

    await waitFor(() => {
      expect(screen.getByText('85%')).toBeInTheDocument();
    });
  });

  it('handles copy code functionality', async () => {
    mockSubscribe.mockImplementation((callback) => {
      callback(mockTextChange);
      return { unsubscribe: jest.fn() };
    });

    const mockClipboard = {
      writeText: jest.fn(),
    };
    Object.assign(navigator, {
      clipboard: mockClipboard,
    });

    render(
      <ThemeProvider theme={theme}>
        <AIPairProgramming sessionId="test-session" currentFile="test.ts" />
      </ThemeProvider>
    );

    await waitFor(() => {
      expect(screen.getByText(mockSuggestion.message)).toBeInTheDocument();
    });

    // Expand suggestion
    fireEvent.click(screen.getByText(mockSuggestion.message));

    // Click copy button
    const copyButton = screen.getByTitle('Copy code');
    fireEvent.click(copyButton);

    expect(mockClipboard.writeText).toHaveBeenCalledWith(mockSuggestion.code);
  });
}); 