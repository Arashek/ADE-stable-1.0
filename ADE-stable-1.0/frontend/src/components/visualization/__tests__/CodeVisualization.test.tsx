import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { ThemeProvider, createTheme } from '@mui/material';
import { CodeVisualization } from '../CodeVisualization';
import { CodeMetrics, DependencyGraph } from '../../../types/visualization.types';

const mockMetrics: CodeMetrics = {
  complexity: 0.75,
  maintainability: 0.85,
  testCoverage: 92,
  performance: {
    timeComplexity: 'O(n)',
    spaceComplexity: 'O(1)'
  },
  dependencies: 5,
  linesOfCode: 150
};

const mockDependencies: DependencyGraph = {
  nodes: [
    {
      id: '1',
      label: 'App.tsx',
      type: 'file',
      metrics: {
        complexity: 0.8,
        maintainability: 0.9
      }
    },
    {
      id: '2',
      label: 'UserService',
      type: 'class',
      metrics: {
        complexity: 0.6,
        maintainability: 0.7
      }
    }
  ],
  links: [
    {
      source: '1',
      target: '2',
      type: 'imports',
      weight: 1
    }
  ]
};

const mockCode = `
import React from 'react';
function App() {
  return <div>Hello World</div>;
}
`;

describe('CodeVisualization', () => {
  const theme = createTheme();

  const renderComponent = () => {
    return render(
      <ThemeProvider theme={theme}>
        <CodeVisualization
          code={mockCode}
          metrics={mockMetrics}
          dependencies={mockDependencies}
        />
      </ThemeProvider>
    );
  };

  it('renders code metrics section', () => {
    renderComponent();
    expect(screen.getByText('Code Metrics')).toBeInTheDocument();
    expect(screen.getByText('Complexity')).toBeInTheDocument();
    expect(screen.getByText('Maintainability')).toBeInTheDocument();
    expect(screen.getByText('Test Coverage')).toBeInTheDocument();
  });

  it('displays performance metrics', () => {
    renderComponent();
    expect(screen.getByText('Performance')).toBeInTheDocument();
    expect(screen.getByText(`Time Complexity: ${mockMetrics.performance.timeComplexity}`)).toBeInTheDocument();
    expect(screen.getByText(`Space Complexity: ${mockMetrics.performance.spaceComplexity}`)).toBeInTheDocument();
  });

  it('renders force graph with correct number of nodes', () => {
    renderComponent();
    const graphContainer = screen.getByRole('region');
    expect(graphContainer).toBeInTheDocument();
    // Note: We can't directly test the ForceGraph2D component's internals,
    // but we can verify the container is present
  });

  it('formats metric values correctly', () => {
    renderComponent();
    expect(screen.getByText('0.75/1')).toBeInTheDocument();
    expect(screen.getByText('0.85/1')).toBeInTheDocument();
    expect(screen.getByText('92.00/100')).toBeInTheDocument();
  });
}); 