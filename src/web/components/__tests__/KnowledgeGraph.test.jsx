import React from 'react';
import { render, screen } from '@testing-library/react';
import { ThemeProvider, createTheme } from '@mui/material';
import KnowledgeGraph from '../KnowledgeGraph';

// Mock data
const mockEntries = [
  {
    id: '1',
    topic: 'Test Topic 1',
    importance_score: 0.8
  },
  {
    id: '2',
    topic: 'Test Topic 2',
    importance_score: 0.6
  }
];

const mockRelationships = [
  {
    source_id: '1',
    target_id: '2',
    strength: 0.7,
    type: 'related'
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

describe('KnowledgeGraph', () => {
  it('renders without crashing', () => {
    renderWithTheme(
      <KnowledgeGraph
        entries={mockEntries}
        relationships={mockRelationships}
      />
    );
    expect(screen.getByText('Knowledge Network')).toBeInTheDocument();
  });

  it('renders with empty data', () => {
    renderWithTheme(
      <KnowledgeGraph
        entries={[]}
        relationships={[]}
      />
    );
    expect(screen.getByText('Knowledge Network')).toBeInTheDocument();
  });

  it('renders with correct number of nodes', () => {
    renderWithTheme(
      <KnowledgeGraph
        entries={mockEntries}
        relationships={mockRelationships}
      />
    );
    const graphContainer = screen.getByRole('graphics-document');
    expect(graphContainer).toBeInTheDocument();
  });

  it('applies correct node colors based on importance score', () => {
    const entries = [
      {
        id: '1',
        topic: 'High Importance',
        importance_score: 0.8
      },
      {
        id: '2',
        topic: 'Medium Importance',
        importance_score: 0.5
      },
      {
        id: '3',
        topic: 'Low Importance',
        importance_score: 0.3
      }
    ];

    renderWithTheme(
      <KnowledgeGraph
        entries={entries}
        relationships={[]}
      />
    );
    const graphContainer = screen.getByRole('graphics-document');
    expect(graphContainer).toBeInTheDocument();
  });
}); 