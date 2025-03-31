import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { ThemeProvider, createTheme } from '@mui/material';
import MemoryInterface from '../MemoryInterface';

// Mock the orchestrator
const mockOrchestrator = {
  getMemoryStats: jest.fn(),
  getAgentExpertise: jest.fn(),
  searchKnowledge: jest.fn(),
  shareKnowledge: jest.fn(),
  updateKnowledge: jest.fn(),
  deleteKnowledge: jest.fn()
};

// Mock data
const mockStats = {
  total_entries: 100,
  total_agents: 5,
  total_conversations: 20,
  average_entries_per_agent: 20,
  last_sync: new Date().toISOString()
};

const mockExpertise = {
  'python': 0.8,
  'javascript': 0.6,
  'typescript': 0.7
};

const mockSearchResults = [
  {
    id: '1',
    topic: 'Test Topic 1',
    content: 'Test Content 1',
    tags: ['test', 'unit'],
    importance_score: 0.8
  },
  {
    id: '2',
    topic: 'Test Topic 2',
    content: 'Test Content 2',
    tags: ['test', 'integration'],
    importance_score: 0.6
  }
];

// Helper function to render with theme
const renderWithTheme = (component) => {
  const theme = createTheme();
  return render(
    <ThemeProvider theme={theme}>
      {component}
    </ThemeProvider>
  );
};

describe('MemoryInterface', () => {
  beforeEach(() => {
    // Reset all mocks before each test
    jest.clearAllMocks();
    
    // Setup default mock implementations
    mockOrchestrator.getMemoryStats.mockResolvedValue(mockStats);
    mockOrchestrator.getAgentExpertise.mockResolvedValue(mockExpertise);
    mockOrchestrator.searchKnowledge.mockResolvedValue(mockSearchResults);
  });

  it('renders without crashing', () => {
    renderWithTheme(<MemoryInterface orchestrator={mockOrchestrator} />);
    expect(screen.getByText('Memory Interface')).toBeInTheDocument();
  });

  it('loads memory stats on mount', async () => {
    renderWithTheme(<MemoryInterface orchestrator={mockOrchestrator} />);
    
    await waitFor(() => {
      expect(mockOrchestrator.getMemoryStats).toHaveBeenCalled();
    });

    expect(screen.getByText('100')).toBeInTheDocument();
    expect(screen.getByText('5')).toBeInTheDocument();
  });

  it('loads expertise data on mount', async () => {
    renderWithTheme(<MemoryInterface orchestrator={mockOrchestrator} />);
    
    await waitFor(() => {
      expect(mockOrchestrator.getAgentExpertise).toHaveBeenCalled();
    });

    expect(screen.getByText('python')).toBeInTheDocument();
    expect(screen.getByText('javascript')).toBeInTheDocument();
    expect(screen.getByText('typescript')).toBeInTheDocument();
  });

  it('performs search when search button is clicked', async () => {
    renderWithTheme(<MemoryInterface orchestrator={mockOrchestrator} />);
    
    const searchInput = screen.getByPlaceholderText('Search knowledge...');
    const searchButton = screen.getByRole('button', { name: /search/i });

    fireEvent.change(searchInput, { target: { value: 'test query' } });
    fireEvent.click(searchButton);

    await waitFor(() => {
      expect(mockOrchestrator.searchKnowledge).toHaveBeenCalledWith('test query');
    });

    expect(screen.getByText('Test Topic 1')).toBeInTheDocument();
    expect(screen.getByText('Test Topic 2')).toBeInTheDocument();
  });

  it('performs search when Enter key is pressed', async () => {
    renderWithTheme(<MemoryInterface orchestrator={mockOrchestrator} />);
    
    const searchInput = screen.getByPlaceholderText('Search knowledge...');
    
    fireEvent.change(searchInput, { target: { value: 'test query' } });
    fireEvent.keyPress(searchInput, { key: 'Enter' });

    await waitFor(() => {
      expect(mockOrchestrator.searchKnowledge).toHaveBeenCalledWith('test query');
    });
  });

  it('shows loading state during search', async () => {
    mockOrchestrator.searchKnowledge.mockImplementation(() => new Promise(resolve => setTimeout(resolve, 100)));
    
    renderWithTheme(<MemoryInterface orchestrator={mockOrchestrator} />);
    
    const searchInput = screen.getByPlaceholderText('Search knowledge...');
    const searchButton = screen.getByRole('button', { name: /search/i });

    fireEvent.change(searchInput, { target: { value: 'test query' } });
    fireEvent.click(searchButton);

    expect(screen.getByRole('progressbar')).toBeInTheDocument();

    await waitFor(() => {
      expect(screen.queryByRole('progressbar')).not.toBeInTheDocument();
    });
  });

  it('shows error message when search fails', async () => {
    mockOrchestrator.searchKnowledge.mockRejectedValue(new Error('Search failed'));
    
    renderWithTheme(<MemoryInterface orchestrator={mockOrchestrator} />);
    
    const searchInput = screen.getByPlaceholderText('Search knowledge...');
    const searchButton = screen.getByRole('button', { name: /search/i });

    fireEvent.change(searchInput, { target: { value: 'test query' } });
    fireEvent.click(searchButton);

    await waitFor(() => {
      expect(screen.getByText('Search failed')).toBeInTheDocument();
    });
  });

  it('opens edit dialog when edit button is clicked', async () => {
    renderWithTheme(<MemoryInterface orchestrator={mockOrchestrator} />);
    
    // Perform search to show results
    const searchInput = screen.getByPlaceholderText('Search knowledge...');
    fireEvent.change(searchInput, { target: { value: 'test query' } });
    fireEvent.keyPress(searchInput, { key: 'Enter' });

    await waitFor(() => {
      expect(screen.getByText('Test Topic 1')).toBeInTheDocument();
    });

    // Click edit button
    const editButtons = screen.getAllByRole('button', { name: /edit/i });
    fireEvent.click(editButtons[0]);

    expect(screen.getByText('Edit Knowledge Entry')).toBeInTheDocument();
    expect(screen.getByRole('textbox')).toHaveValue('Test Content 1');
  });

  it('saves edited content when save button is clicked', async () => {
    mockOrchestrator.updateKnowledge.mockResolvedValue(true);
    
    renderWithTheme(<MemoryInterface orchestrator={mockOrchestrator} />);
    
    // Perform search and open edit dialog
    const searchInput = screen.getByPlaceholderText('Search knowledge...');
    fireEvent.change(searchInput, { target: { value: 'test query' } });
    fireEvent.keyPress(searchInput, { key: 'Enter' });

    await waitFor(() => {
      expect(screen.getByText('Test Topic 1')).toBeInTheDocument();
    });

    const editButtons = screen.getAllByRole('button', { name: /edit/i });
    fireEvent.click(editButtons[0]);

    // Edit content and save
    const editInput = screen.getByRole('textbox');
    fireEvent.change(editInput, { target: { value: 'Updated content' } });
    fireEvent.click(screen.getByText('Save'));

    await waitFor(() => {
      expect(mockOrchestrator.updateKnowledge).toHaveBeenCalledWith('1', 'Updated content');
    });
  });

  it('deletes entry when delete button is clicked', async () => {
    mockOrchestrator.deleteKnowledge.mockResolvedValue(true);
    
    renderWithTheme(<MemoryInterface orchestrator={mockOrchestrator} />);
    
    // Perform search
    const searchInput = screen.getByPlaceholderText('Search knowledge...');
    fireEvent.change(searchInput, { target: { value: 'test query' } });
    fireEvent.keyPress(searchInput, { key: 'Enter' });

    await waitFor(() => {
      expect(screen.getByText('Test Topic 1')).toBeInTheDocument();
    });

    // Click delete button
    const deleteButtons = screen.getAllByRole('button', { name: /delete/i });
    fireEvent.click(deleteButtons[0]);

    // Confirm deletion
    expect(window.confirm).toHaveBeenCalled();
    
    await waitFor(() => {
      expect(mockOrchestrator.deleteKnowledge).toHaveBeenCalledWith('1');
    });
  });

  it('shares knowledge when share button is clicked', async () => {
    mockOrchestrator.shareKnowledge.mockResolvedValue(true);
    
    renderWithTheme(<MemoryInterface orchestrator={mockOrchestrator} />);
    
    // Perform search
    const searchInput = screen.getByPlaceholderText('Search knowledge...');
    fireEvent.change(searchInput, { target: { value: 'test query' } });
    fireEvent.keyPress(searchInput, { key: 'Enter' });

    await waitFor(() => {
      expect(screen.getByText('Test Topic 1')).toBeInTheDocument();
    });

    // Click share button
    const shareButtons = screen.getAllByRole('button', { name: /share/i });
    fireEvent.click(shareButtons[0]);

    await waitFor(() => {
      expect(mockOrchestrator.shareKnowledge).toHaveBeenCalledWith('1');
    });
  });

  it('switches between tabs correctly', () => {
    renderWithTheme(<MemoryInterface orchestrator={mockOrchestrator} />);
    
    // Check initial tab
    expect(screen.getByText('Search')).toHaveAttribute('aria-selected', 'true');

    // Switch to Statistics tab
    fireEvent.click(screen.getByText('Statistics'));
    expect(screen.getByText('Memory Statistics')).toBeInTheDocument();

    // Switch to Expertise tab
    fireEvent.click(screen.getByText('Expertise'));
    expect(screen.getByText('Agent Expertise')).toBeInTheDocument();

    // Switch to History tab
    fireEvent.click(screen.getByText('History'));
    expect(screen.getByText('History view coming soon...')).toBeInTheDocument();
  });
}); 