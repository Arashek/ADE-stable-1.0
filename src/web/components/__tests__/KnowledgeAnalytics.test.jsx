import React from 'react';
import { render, screen } from '@testing-library/react';
import { ThemeProvider, createTheme } from '@mui/material';
import KnowledgeAnalytics from '../KnowledgeAnalytics';

// Mock data
const mockEntries = [
  {
    id: '1',
    topic: 'Test Topic 1',
    content: 'Test Content 1',
    tags: ['test', 'unit'],
    created_at: '2024-01-01T00:00:00Z',
    importance_score: 0.8
  },
  {
    id: '2',
    topic: 'Test Topic 2',
    content: 'Test Content 2',
    tags: ['test', 'integration'],
    created_at: '2024-01-02T00:00:00Z',
    importance_score: 0.6
  }
];

const mockStats = {
  total_entries: 100,
  total_agents: 5,
  total_conversations: 20,
  average_entries_per_agent: 20,
  last_sync: '2024-01-03T00:00:00Z',
  expertise_by_domain: {
    'python': 0.8,
    'javascript': 0.6,
    'typescript': 0.7
  }
};

const mockTimeRange = [
  '2024-01-01T00:00:00Z',
  '2024-01-02T00:00:00Z',
  '2024-01-03T00:00:00Z'
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

describe('KnowledgeAnalytics', () => {
  it('renders without crashing', () => {
    renderWithTheme(
      <KnowledgeAnalytics
        entries={mockEntries}
        stats={mockStats}
        timeRange={mockTimeRange}
      />
    );
    expect(screen.getByText('Knowledge Analytics')).toBeInTheDocument();
  });

  it('renders with empty data', () => {
    renderWithTheme(
      <KnowledgeAnalytics
        entries={[]}
        stats={{
          total_entries: 0,
          total_agents: 0,
          total_conversations: 0,
          average_entries_per_agent: 0,
          last_sync: new Date().toISOString(),
          expertise_by_domain: {}
        }}
        timeRange={[]}
      />
    );
    expect(screen.getByText('Knowledge Analytics')).toBeInTheDocument();
  });

  it('displays all chart sections', () => {
    renderWithTheme(
      <KnowledgeAnalytics
        entries={mockEntries}
        stats={mockStats}
        timeRange={mockTimeRange}
      />
    );
    
    expect(screen.getByText('Tag Distribution')).toBeInTheDocument();
    expect(screen.getByText('Knowledge Growth')).toBeInTheDocument();
    expect(screen.getByText('Expertise Distribution')).toBeInTheDocument();
  });

  it('displays correct statistics', () => {
    renderWithTheme(
      <KnowledgeAnalytics
        entries={mockEntries}
        stats={mockStats}
        timeRange={mockTimeRange}
      />
    );
    
    expect(screen.getByText('100')).toBeInTheDocument();
    expect(screen.getByText('5')).toBeInTheDocument();
    expect(screen.getByText('3')).toBeInTheDocument(); // Total unique tags
  });

  it('displays info tooltip', () => {
    renderWithTheme(
      <KnowledgeAnalytics
        entries={mockEntries}
        stats={mockStats}
        timeRange={mockTimeRange}
      />
    );
    
    const infoButton = screen.getByRole('button');
    expect(infoButton).toBeInTheDocument();
  });

  it('renders all charts', () => {
    renderWithTheme(
      <KnowledgeAnalytics
        entries={mockEntries}
        stats={mockStats}
        timeRange={mockTimeRange}
      />
    );
    
    const charts = screen.getAllByRole('img');
    expect(charts).toHaveLength(3); // Pie chart, Bar chart, and Expertise chart
  });

  it('displays correct date format for last sync', () => {
    renderWithTheme(
      <KnowledgeAnalytics
        entries={mockEntries}
        stats={mockStats}
        timeRange={mockTimeRange}
      />
    );
    
    const lastSyncDate = new Date(mockStats.last_sync).toLocaleDateString();
    expect(screen.getByText(lastSyncDate)).toBeInTheDocument();
  });

  it('calculates tag distribution correctly', () => {
    renderWithTheme(
      <KnowledgeAnalytics
        entries={mockEntries}
        stats={mockStats}
        timeRange={mockTimeRange}
      />
    );
    
    // Check if all unique tags are displayed
    const uniqueTags = [...new Set(mockEntries.flatMap(entry => entry.tags))];
    uniqueTags.forEach(tag => {
      expect(screen.getByText(tag)).toBeInTheDocument();
    });
  });
}); 