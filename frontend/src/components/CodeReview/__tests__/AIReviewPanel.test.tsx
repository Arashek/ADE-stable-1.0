import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import AIReviewPanel from '../AIReviewPanel';
import { CodeQualityService } from '../../../services/codeAnalysis/CodeQualityService';

// Mock the CodeQualityService
jest.mock('../../../services/codeAnalysis/CodeQualityService', () => ({
  CodeQualityService: {
    getInstance: jest.fn(),
  },
}));

const mockAnalysis = {
  metrics: {
    complexity: 0.75,
    maintainability: 0.85,
    testability: 0.90,
    security: 0.95,
    performance: 0.80,
  },
  issues: [
    {
      id: '1',
      type: 'warning',
      message: 'Variable is never used',
      line: 10,
      column: 5,
      severity: 2,
      rule: 'no-unused-vars',
      fix: {
        description: 'Remove unused variable',
        code: 'const x = 5;',
      },
    },
  ],
  suggestions: ['Consider adding type annotations'],
  aiInsights: ['The code could benefit from better error handling'],
};

const theme = createTheme();

describe('AIReviewPanel', () => {
  const mockOnFixApply = jest.fn();
  const mockOnNavigateToIssue = jest.fn();
  let mockSubscribeToAnalysis: jest.Mock;
  let mockGetCachedAnalysis: jest.Mock;

  beforeEach(() => {
    mockSubscribeToAnalysis = jest.fn();
    mockGetCachedAnalysis = jest.fn();

    (CodeQualityService.getInstance as jest.Mock).mockReturnValue({
      subscribeToAnalysis: mockSubscribeToAnalysis,
      getCachedAnalysis: mockGetCachedAnalysis,
    });

    mockSubscribeToAnalysis.mockImplementation((_, callback) => {
      callback(mockAnalysis);
      return () => {};
    });
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  it('renders loading state initially', () => {
    mockGetCachedAnalysis.mockReturnValue(null);
    
    render(
      <ThemeProvider theme={theme}>
        <AIReviewPanel
          filePath="test.ts"
          onFixApply={mockOnFixApply}
          onNavigateToIssue={mockOnNavigateToIssue}
        />
      </ThemeProvider>
    );

    expect(screen.getByRole('progressbar')).toBeInTheDocument();
  });

  it('displays metrics when analysis is available', async () => {
    mockGetCachedAnalysis.mockReturnValue(mockAnalysis);

    render(
      <ThemeProvider theme={theme}>
        <AIReviewPanel
          filePath="test.ts"
          onFixApply={mockOnFixApply}
          onNavigateToIssue={mockOnNavigateToIssue}
        />
      </ThemeProvider>
    );

    // Check each metric individually
    await screen.findByText('75%');
    await screen.findByText('85%');
    await screen.findByText('90%');
    await screen.findByText('95%');
    await screen.findByText('80%');
  });

  it('displays issues and allows expanding them', async () => {
    mockGetCachedAnalysis.mockReturnValue(mockAnalysis);

    render(
      <ThemeProvider theme={theme}>
        <AIReviewPanel
          filePath="test.ts"
          onFixApply={mockOnFixApply}
          onNavigateToIssue={mockOnNavigateToIssue}
        />
      </ThemeProvider>
    );

    await waitFor(() => {
      expect(screen.getByText('Variable is never used')).toBeInTheDocument();
    });

    // Click to expand the issue
    fireEvent.click(screen.getByText('Variable is never used'));

    await waitFor(() => {
      expect(screen.getByText('Remove unused variable')).toBeInTheDocument();
    });
  });

  it('calls onFixApply when fix button is clicked', async () => {
    mockGetCachedAnalysis.mockReturnValue(mockAnalysis);

    render(
      <ThemeProvider theme={theme}>
        <AIReviewPanel
          filePath="test.ts"
          onFixApply={mockOnFixApply}
          onNavigateToIssue={mockOnNavigateToIssue}
        />
      </ThemeProvider>
    );

    // Click to expand the issue
    fireEvent.click(screen.getByText('Variable is never used'));

    // Click the fix button
    const fixButton = await screen.findByText('Apply Fix');
    fireEvent.click(fixButton);

    expect(mockOnFixApply).toHaveBeenCalledWith({
      description: 'Remove unused variable',
      code: 'const x = 5;',
    });
  });

  it('displays AI insights when available', async () => {
    mockGetCachedAnalysis.mockReturnValue(mockAnalysis);

    render(
      <ThemeProvider theme={theme}>
        <AIReviewPanel
          filePath="test.ts"
          onFixApply={mockOnFixApply}
          onNavigateToIssue={mockOnNavigateToIssue}
        />
      </ThemeProvider>
    );

    await screen.findByText('AI Insights');
    await screen.findByText('The code could benefit from better error handling');
  });

  it('shows no issues message when there are no issues', async () => {
    const noIssuesAnalysis = {
      ...mockAnalysis,
      issues: [],
    };

    mockGetCachedAnalysis.mockReturnValue(noIssuesAnalysis);

    render(
      <ThemeProvider theme={theme}>
        <AIReviewPanel
          filePath="test.ts"
          onFixApply={mockOnFixApply}
          onNavigateToIssue={mockOnNavigateToIssue}
        />
      </ThemeProvider>
    );

    await waitFor(() => {
      expect(screen.getByText('No issues found')).toBeInTheDocument();
    });
  });
}); 