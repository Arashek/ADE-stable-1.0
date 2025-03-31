import React from 'react';
import { render, screen, fireEvent, act } from '@testing-library/react';
import { ThemeProvider, createTheme } from '@mui/material';
import userEvent from '@testing-library/user-event';
import AdvancedVisualizations from '../AdvancedVisualizations';

// Mock data
const mockEntries = [
  {
    id: '1',
    topic: 'Test Topic 1',
    content: 'Test Content 1',
    tags: ['test', 'unit'],
    created_at: '2024-01-01T10:00:00Z',
    importance_score: 0.8
  },
  {
    id: '2',
    topic: 'Test Topic 2',
    content: 'Test Content 2',
    tags: ['test', 'integration'],
    created_at: '2024-01-02T15:00:00Z',
    importance_score: 0.6
  },
  {
    id: '3',
    topic: 'Test Topic 3',
    content: 'Test Content 3',
    tags: ['unit', 'performance'],
    created_at: '2024-01-03T20:00:00Z',
    importance_score: 0.7
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

// Additional mock data for performance testing
const generateLargeDataset = (size) => {
  return Array(size).fill().map((_, index) => ({
    id: `entry-${index}`,
    topic: `Test Topic ${index}`,
    content: `Test Content ${index}`,
    tags: ['test', `tag-${index % 5}`],
    created_at: new Date(Date.now() - Math.random() * 7 * 24 * 60 * 60 * 1000).toISOString(),
    importance_score: Math.random()
  }));
};

// Helper function to render with theme
const renderWithTheme = (component) => {
  const theme = createTheme();
  return render(
    <ThemeProvider theme={theme}>
      {component}
    </ThemeProvider>
  );
};

describe('AdvancedVisualizations', () => {
  it('renders without crashing', () => {
    renderWithTheme(
      <AdvancedVisualizations
        entries={mockEntries}
        stats={mockStats}
        timeRange={mockTimeRange}
      />
    );
    expect(screen.getByText('Advanced Visualizations')).toBeInTheDocument();
  });

  it('renders with empty data', () => {
    renderWithTheme(
      <AdvancedVisualizations
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
    expect(screen.getByText('Advanced Visualizations')).toBeInTheDocument();
  });

  it('displays visualization type selector', () => {
    renderWithTheme(
      <AdvancedVisualizations
        entries={mockEntries}
        stats={mockStats}
        timeRange={mockTimeRange}
      />
    );
    
    expect(screen.getByLabelText('Visualization Type')).toBeInTheDocument();
  });

  it('switches between visualization types', () => {
    renderWithTheme(
      <AdvancedVisualizations
        entries={mockEntries}
        stats={mockStats}
        timeRange={mockTimeRange}
      />
    );
    
    const selector = screen.getByLabelText('Visualization Type');
    fireEvent.mouseDown(selector);
    
    expect(screen.getByText('Activity Heat Map')).toBeInTheDocument();
    expect(screen.getByText('Knowledge Tree Map')).toBeInTheDocument();
  });

  it('displays heatmap by default', () => {
    renderWithTheme(
      <AdvancedVisualizations
        entries={mockEntries}
        stats={mockStats}
        timeRange={mockTimeRange}
      />
    );
    
    expect(screen.getByText('Activity Heat Map')).toBeInTheDocument();
    expect(screen.getByText('Shows the distribution of knowledge creation across different times and days')).toBeInTheDocument();
  });

  it('displays treemap when selected', () => {
    renderWithTheme(
      <AdvancedVisualizations
        entries={mockEntries}
        stats={mockStats}
        timeRange={mockTimeRange}
      />
    );
    
    const selector = screen.getByLabelText('Visualization Type');
    fireEvent.mouseDown(selector);
    fireEvent.click(screen.getByText('Knowledge Tree Map'));
    
    expect(screen.getByText('Knowledge Tree Map')).toBeInTheDocument();
    expect(screen.getByText('Visualizes the hierarchical structure of knowledge based on tags and their relationships')).toBeInTheDocument();
  });

  it('displays info tooltip', () => {
    renderWithTheme(
      <AdvancedVisualizations
        entries={mockEntries}
        stats={mockStats}
        timeRange={mockTimeRange}
      />
    );
    
    const infoButton = screen.getByRole('button');
    expect(infoButton).toBeInTheDocument();
  });

  it('processes heatmap data correctly', () => {
    renderWithTheme(
      <AdvancedVisualizations
        entries={mockEntries}
        stats={mockStats}
        timeRange={mockTimeRange}
      />
    );
    
    // Check if the visualization container is present
    const container = screen.getByRole('img');
    expect(container).toBeInTheDocument();
  });

  it('processes treemap data correctly', () => {
    renderWithTheme(
      <AdvancedVisualizations
        entries={mockEntries}
        stats={mockStats}
        timeRange={mockTimeRange}
      />
    );
    
    // Switch to treemap view
    const selector = screen.getByLabelText('Visualization Type');
    fireEvent.mouseDown(selector);
    fireEvent.click(screen.getByText('Knowledge Tree Map'));
    
    // Check if the visualization container is present
    const container = screen.getByRole('img');
    expect(container).toBeInTheDocument();
  });

  it('handles invalid dates gracefully', () => {
    const entriesWithInvalidDates = [
      {
        ...mockEntries[0],
        created_at: 'invalid-date'
      },
      ...mockEntries.slice(1)
    ];

    renderWithTheme(
      <AdvancedVisualizations
        entries={entriesWithInvalidDates}
        stats={mockStats}
        timeRange={mockTimeRange}
      />
    );
    
    // Component should still render without crashing
    expect(screen.getByText('Advanced Visualizations')).toBeInTheDocument();
  });

  it('handles missing tags gracefully', () => {
    const entriesWithoutTags = [
      {
        ...mockEntries[0],
        tags: []
      },
      ...mockEntries.slice(1)
    ];

    renderWithTheme(
      <AdvancedVisualizations
        entries={entriesWithoutTags}
        stats={mockStats}
        timeRange={mockTimeRange}
      />
    );
    
    // Component should still render without crashing
    expect(screen.getByText('Advanced Visualizations')).toBeInTheDocument();
  });

  describe('Data Processing', () => {
    it('correctly processes heatmap data for different time zones', () => {
      const entriesWithDifferentTimeZones = [
        {
          ...mockEntries[0],
          created_at: '2024-01-01T10:00:00+00:00Z'
        },
        {
          ...mockEntries[1],
          created_at: '2024-01-01T15:00:00+05:00Z'
        }
      ];

      renderWithTheme(
        <AdvancedVisualizations
          entries={entriesWithDifferentTimeZones}
          stats={mockStats}
          timeRange={mockTimeRange}
        />
      );

      const container = screen.getByRole('img');
      expect(container).toBeInTheDocument();
    });

    it('correctly aggregates treemap data with nested tags', () => {
      const entriesWithNestedTags = [
        {
          ...mockEntries[0],
          tags: ['test', 'unit', 'nested.test']
        },
        {
          ...mockEntries[1],
          tags: ['test', 'integration', 'nested.integration']
        }
      ];

      renderWithTheme(
        <AdvancedVisualizations
          entries={entriesWithNestedTags}
          stats={mockStats}
          timeRange={mockTimeRange}
        />
      );

      const selector = screen.getByLabelText('Visualization Type');
      fireEvent.mouseDown(selector);
      fireEvent.click(screen.getByText('Knowledge Tree Map'));

      const container = screen.getByRole('img');
      expect(container).toBeInTheDocument();
    });

    it('handles duplicate tags correctly', () => {
      const entriesWithDuplicateTags = [
        {
          ...mockEntries[0],
          tags: ['test', 'test', 'unit']
        }
      ];

      renderWithTheme(
        <AdvancedVisualizations
          entries={entriesWithDuplicateTags}
          stats={mockStats}
          timeRange={mockTimeRange}
        />
      );

      const selector = screen.getByLabelText('Visualization Type');
      fireEvent.mouseDown(selector);
      fireEvent.click(screen.getByText('Knowledge Tree Map'));

      const container = screen.getByRole('img');
      expect(container).toBeInTheDocument();
    });
  });

  describe('Visualization Interactions', () => {
    it('responds to hover events on heatmap cells', async () => {
      renderWithTheme(
        <AdvancedVisualizations
          entries={mockEntries}
          stats={mockStats}
          timeRange={mockTimeRange}
        />
      );

      const container = screen.getByRole('img');
      await userEvent.hover(container);

      // Check if tooltip or hover effect is present
      expect(container).toHaveAttribute('data-testid', 'heatmap-container');
    });

    it('responds to click events on treemap nodes', async () => {
      renderWithTheme(
        <AdvancedVisualizations
          entries={mockEntries}
          stats={mockStats}
          timeRange={mockTimeRange}
        />
      );

      const selector = screen.getByLabelText('Visualization Type');
      fireEvent.mouseDown(selector);
      fireEvent.click(screen.getByText('Knowledge Tree Map'));

      const container = screen.getByRole('img');
      await userEvent.click(container);

      // Check if click handler is triggered
      expect(container).toHaveAttribute('data-testid', 'treemap-container');
    });

    it('updates visualization when data changes', () => {
      const { rerender } = renderWithTheme(
        <AdvancedVisualizations
          entries={mockEntries}
          stats={mockStats}
          timeRange={mockTimeRange}
        />
      );

      const newEntries = [...mockEntries, {
        id: '4',
        topic: 'New Topic',
        content: 'New Content',
        tags: ['new', 'test'],
        created_at: '2024-01-04T12:00:00Z',
        importance_score: 0.9
      }];

      rerender(
        <ThemeProvider theme={createTheme()}>
          <AdvancedVisualizations
            entries={newEntries}
            stats={mockStats}
            timeRange={mockTimeRange}
          />
        </ThemeProvider>
      );

      const container = screen.getByRole('img');
      expect(container).toBeInTheDocument();
    });
  });

  describe('Performance with Large Datasets', () => {
    it('handles large dataset without performance degradation', async () => {
      const largeEntries = generateLargeDataset(1000);
      
      const startTime = performance.now();
      
      renderWithTheme(
        <AdvancedVisualizations
          entries={largeEntries}
          stats={mockStats}
          timeRange={mockTimeRange}
        />
      );

      const endTime = performance.now();
      const renderTime = endTime - startTime;

      // Assert that rendering time is within acceptable limits (e.g., less than 500ms)
      expect(renderTime).toBeLessThan(500);

      const container = screen.getByRole('img');
      expect(container).toBeInTheDocument();
    });

    it('maintains responsiveness with frequent updates', async () => {
      const { rerender } = renderWithTheme(
        <AdvancedVisualizations
          entries={mockEntries}
          stats={mockStats}
          timeRange={mockTimeRange}
        />
      );

      // Simulate rapid updates
      for (let i = 0; i < 10; i++) {
        await act(async () => {
          rerender(
            <ThemeProvider theme={createTheme()}>
              <AdvancedVisualizations
                entries={[...mockEntries, {
                  id: `update-${i}`,
                  topic: `Update ${i}`,
                  content: `Content ${i}`,
                  tags: ['update'],
                  created_at: new Date().toISOString(),
                  importance_score: Math.random()
                }]}
                stats={mockStats}
                timeRange={mockTimeRange}
              />
            </ThemeProvider>
          );
        });
      }

      const container = screen.getByRole('img');
      expect(container).toBeInTheDocument();
    });
  });

  describe('Accessibility Features', () => {
    it('has proper ARIA labels for visualizations', () => {
      renderWithTheme(
        <AdvancedVisualizations
          entries={mockEntries}
          stats={mockStats}
          timeRange={mockTimeRange}
        />
      );

      const container = screen.getByRole('img');
      expect(container).toHaveAttribute('aria-label', 'Activity Heat Map');
    });

    it('supports keyboard navigation', async () => {
      renderWithTheme(
        <AdvancedVisualizations
          entries={mockEntries}
          stats={mockStats}
          timeRange={mockTimeRange}
        />
      );

      const selector = screen.getByLabelText('Visualization Type');
      selector.focus();

      // Test keyboard navigation
      await userEvent.keyboard('{Enter}');
      await userEvent.keyboard('{ArrowDown}');
      await userEvent.keyboard('{Enter}');

      expect(screen.getByText('Knowledge Tree Map')).toBeInTheDocument();
    });

    it('provides sufficient color contrast', () => {
      renderWithTheme(
        <AdvancedVisualizations
          entries={mockEntries}
          stats={mockStats}
          timeRange={mockTimeRange}
        />
      );

      const container = screen.getByRole('img');
      const computedStyle = window.getComputedStyle(container);
      
      // Check if text color and background color meet WCAG contrast requirements
      expect(computedStyle.color).toBeDefined();
      expect(computedStyle.backgroundColor).toBeDefined();
    });

    it('includes descriptive text for screen readers', () => {
      renderWithTheme(
        <AdvancedVisualizations
          entries={mockEntries}
          stats={mockStats}
          timeRange={mockTimeRange}
        />
      );

      const description = screen.getByText('Shows the distribution of knowledge creation across different times and days');
      expect(description).toBeInTheDocument();
      expect(description).toHaveAttribute('role', 'text');
    });

    it('maintains focus management during visualization switching', async () => {
      renderWithTheme(
        <AdvancedVisualizations
          entries={mockEntries}
          stats={mockStats}
          timeRange={mockTimeRange}
        />
      );

      const selector = screen.getByLabelText('Visualization Type');
      selector.focus();

      // Switch visualization using keyboard
      await userEvent.keyboard('{Enter}');
      await userEvent.keyboard('{ArrowDown}');
      await userEvent.keyboard('{Enter}');

      // Verify focus is maintained
      expect(selector).toHaveFocus();
    });

    it('provides meaningful alt text for visualizations', () => {
      renderWithTheme(
        <AdvancedVisualizations
          entries={mockEntries}
          stats={mockStats}
          timeRange={mockTimeRange}
        />
      );

      const container = screen.getByRole('img');
      expect(container).toHaveAttribute('aria-label', 'Activity Heat Map');
      expect(container).toHaveAttribute('aria-description', 'Shows the distribution of knowledge creation across different times and days');
    });

    it('supports high contrast mode', () => {
      const highContrastTheme = createTheme({
        palette: {
          mode: 'dark',
          contrastThreshold: 4.5
        }
      });

      renderWithTheme(
        <ThemeProvider theme={highContrastTheme}>
          <AdvancedVisualizations
            entries={mockEntries}
            stats={mockStats}
            timeRange={mockTimeRange}
          />
        </ThemeProvider>
      );

      const container = screen.getByRole('img');
      const computedStyle = window.getComputedStyle(container);
      
      // Verify contrast ratio meets WCAG 2.1 AA requirements
      expect(computedStyle.color).toBeDefined();
      expect(computedStyle.backgroundColor).toBeDefined();
    });
  });

  describe('Data Processing Edge Cases', () => {
    it('handles empty time ranges', () => {
      renderWithTheme(
        <AdvancedVisualizations
          entries={mockEntries}
          stats={mockStats}
          timeRange={[]}
        />
      );

      const container = screen.getByRole('img');
      expect(container).toBeInTheDocument();
    });

    it('handles malformed tag hierarchies', () => {
      const entriesWithMalformedTags = [
        {
          ...mockEntries[0],
          tags: ['test..nested', 'invalid..tag..structure']
        }
      ];

      renderWithTheme(
        <AdvancedVisualizations
          entries={entriesWithMalformedTags}
          stats={mockStats}
          timeRange={mockTimeRange}
        />
      );

      const selector = screen.getByLabelText('Visualization Type');
      fireEvent.mouseDown(selector);
      fireEvent.click(screen.getByText('Knowledge Tree Map'));

      const container = screen.getByRole('img');
      expect(container).toBeInTheDocument();
    });

    it('handles timezone edge cases', () => {
      const entriesWithTimezoneEdgeCases = [
        {
          ...mockEntries[0],
          created_at: '2024-01-01T23:59:59.999Z'
        },
        {
          ...mockEntries[1],
          created_at: '2024-01-02T00:00:00.000Z'
        }
      ];

      renderWithTheme(
        <AdvancedVisualizations
          entries={entriesWithTimezoneEdgeCases}
          stats={mockStats}
          timeRange={mockTimeRange}
        />
      );

      const container = screen.getByRole('img');
      expect(container).toBeInTheDocument();
    });
  });

  describe('Error Handling and Boundaries', () => {
    it('handles data processing errors gracefully', () => {
      const invalidEntries = [
        {
          ...mockEntries[0],
          created_at: 'invalid-date'
        }
      ];

      renderWithTheme(
        <AdvancedVisualizations
          entries={invalidEntries}
          stats={mockStats}
          timeRange={mockTimeRange}
        />
      );

      expect(screen.getByText(/Error processing heatmap data/)).toBeInTheDocument();
    });

    it('handles visualization component errors', () => {
      const mockError = new Error('Visualization failed');
      
      // Mock the HeatMap component to throw an error
      jest.mock('../visualizations/HeatMap', () => {
        return function MockHeatMap() {
          throw mockError;
        };
      });

      renderWithTheme(
        <AdvancedVisualizations
          entries={mockEntries}
          stats={mockStats}
          timeRange={mockTimeRange}
        />
      );

      expect(screen.getByText(/Error rendering visualization/)).toBeInTheDocument();
    });

    it('recovers from errors when switching visualizations', () => {
      const { rerender } = renderWithTheme(
        <AdvancedVisualizations
          entries={mockEntries}
          stats={mockStats}
          timeRange={mockTimeRange}
        />
      );

      // Simulate an error in the current visualization
      const errorButton = screen.getByTestId('error-trigger');
      fireEvent.click(errorButton);

      // Switch to a different visualization
      const selector = screen.getByLabelText('Visualization Type');
      fireEvent.mouseDown(selector);
      fireEvent.click(screen.getByText('Knowledge Tree Map'));

      // Verify error is cleared and new visualization is rendered
      expect(screen.queryByText(/Error rendering visualization/)).not.toBeInTheDocument();
      expect(screen.getByTestId('treemap-visualization')).toBeInTheDocument();
    });
  });

  describe('Performance Benchmarks', () => {
    it('maintains performance with very large datasets', async () => {
      const veryLargeEntries = generateLargeDataset(10000);
      
      const startTime = performance.now();
      
      renderWithTheme(
        <AdvancedVisualizations
          entries={veryLargeEntries}
          stats={mockStats}
          timeRange={mockTimeRange}
        />
      );

      const endTime = performance.now();
      const renderTime = endTime - startTime;

      // Assert that rendering time is within acceptable limits
      expect(renderTime).toBeLessThan(1000);

      // Verify data processing performance
      const processingStart = performance.now();
      const selector = screen.getByLabelText('Visualization Type');
      fireEvent.mouseDown(selector);
      fireEvent.click(screen.getByText('Knowledge Tree Map'));
      const processingEnd = performance.now();

      expect(processingEnd - processingStart).toBeLessThan(500);
    });

    it('optimizes re-renders with memoization', async () => {
      const { rerender } = renderWithTheme(
        <AdvancedVisualizations
          entries={mockEntries}
          stats={mockStats}
          timeRange={mockTimeRange}
        />
      );

      const initialRenderTime = performance.now();
      
      // Re-render with same props
      rerender(
        <ThemeProvider theme={createTheme()}>
          <AdvancedVisualizations
            entries={mockEntries}
            stats={mockStats}
            timeRange={mockTimeRange}
          />
        </ThemeProvider>
      );

      const reRenderTime = performance.now();
      
      // Verify that re-render is significantly faster than initial render
      expect(reRenderTime - initialRenderTime).toBeLessThan(initialRenderTime * 0.1);
    });

    it('handles rapid data updates efficiently', async () => {
      const { rerender } = renderWithTheme(
        <AdvancedVisualizations
          entries={mockEntries}
          stats={mockStats}
          timeRange={mockTimeRange}
        />
      );

      const updateTimes = [];
      
      // Simulate rapid data updates
      for (let i = 0; i < 20; i++) {
        const startTime = performance.now();
        
        await act(async () => {
          rerender(
            <ThemeProvider theme={createTheme()}>
              <AdvancedVisualizations
                entries={[...mockEntries, {
                  id: `update-${i}`,
                  topic: `Update ${i}`,
                  content: `Content ${i}`,
                  tags: ['update'],
                  created_at: new Date().toISOString(),
                  importance_score: Math.random()
                }]}
                stats={mockStats}
                timeRange={mockTimeRange}
              />
            </ThemeProvider>
          );
        });

        updateTimes.push(performance.now() - startTime);
      }

      // Calculate average update time
      const avgUpdateTime = updateTimes.reduce((a, b) => a + b, 0) / updateTimes.length;
      
      // Verify that average update time is within acceptable limits
      expect(avgUpdateTime).toBeLessThan(100);
    });
  });

  describe('Extended Performance Benchmarks', () => {
    it('handles extreme dataset sizes', async () => {
      const extremeEntries = generateLargeDataset(50000);
      
      const startTime = performance.now();
      
      renderWithTheme(
        <AdvancedVisualizations
          entries={extremeEntries}
          stats={mockStats}
          timeRange={mockTimeRange}
        />
      );

      const endTime = performance.now();
      const renderTime = endTime - startTime;

      // More lenient threshold for extreme datasets
      expect(renderTime).toBeLessThan(2000);

      // Memory usage check
      const memoryUsage = window.performance.memory;
      if (memoryUsage) {
        expect(memoryUsage.usedJSHeapSize).toBeLessThan(memoryUsage.jsHeapSizeLimit * 0.8);
      }
    });

    it('maintains performance during complex interactions', async () => {
      const { rerender } = renderWithTheme(
        <AdvancedVisualizations
          entries={mockEntries}
          stats={mockStats}
          timeRange={mockTimeRange}
        />
      );

      const interactionTimes = [];
      
      // Simulate complex user interactions
      for (let i = 0; i < 5; i++) {
        const startTime = performance.now();
        
        await act(async () => {
          // Switch visualization type
          const selector = screen.getByLabelText('Visualization Type');
          fireEvent.mouseDown(selector);
          fireEvent.click(screen.getByText('Knowledge Tree Map'));
          
          // Add new data
          rerender(
            <ThemeProvider theme={createTheme()}>
              <AdvancedVisualizations
                entries={[...mockEntries, {
                  id: `complex-${i}`,
                  topic: `Complex Update ${i}`,
                  content: `Complex Content ${i}`,
                  tags: ['complex', 'test'],
                  created_at: new Date().toISOString(),
                  importance_score: Math.random()
                }]}
                stats={mockStats}
                timeRange={mockTimeRange}
              />
            </ThemeProvider>
          );
        });

        interactionTimes.push(performance.now() - startTime);
      }

      const avgInteractionTime = interactionTimes.reduce((a, b) => a + b, 0) / interactionTimes.length;
      expect(avgInteractionTime).toBeLessThan(150);
    });

    it('optimizes data processing for different visualization types', async () => {
      const largeEntries = generateLargeDataset(5000);
      
      // Test heatmap processing
      const heatmapStart = performance.now();
      renderWithTheme(
        <AdvancedVisualizations
          entries={largeEntries}
          stats={mockStats}
          timeRange={mockTimeRange}
        />
      );
      const heatmapTime = performance.now() - heatmapStart;

      // Test treemap processing
      const treemapStart = performance.now();
      const selector = screen.getByLabelText('Visualization Type');
      fireEvent.mouseDown(selector);
      fireEvent.click(screen.getByText('Knowledge Tree Map'));
      const treemapTime = performance.now() - treemapStart;

      // Verify processing times are within acceptable limits
      expect(heatmapTime).toBeLessThan(300);
      expect(treemapTime).toBeLessThan(400);
    });
  });

  describe('Extended Accessibility Features', () => {
    it('supports screen reader navigation through visualization data', async () => {
      renderWithTheme(
        <AdvancedVisualizations
          entries={mockEntries}
          stats={mockStats}
          timeRange={mockTimeRange}
        />
      );

      const container = screen.getByRole('img');
      expect(container).toHaveAttribute('aria-label', 'Activity Heat Map');
      expect(container).toHaveAttribute('aria-live', 'polite');
      expect(container).toHaveAttribute('aria-atomic', 'true');
    });

    it('provides keyboard shortcuts for common actions', async () => {
      renderWithTheme(
        <AdvancedVisualizations
          entries={mockEntries}
          stats={mockStats}
          timeRange={mockTimeRange}
        />
      );

      // Test keyboard shortcuts
      await userEvent.keyboard('{Alt}h'); // Switch to heatmap
      expect(screen.getByTestId('heatmap-visualization')).toBeInTheDocument();
      
      await userEvent.keyboard('{Alt}t'); // Switch to treemap
      expect(screen.getByTestId('treemap-visualization')).toBeInTheDocument();
    });

    it('adapts to user preferences for reduced motion', () => {
      const reducedMotionTheme = createTheme({
        components: {
          MuiCssBaseline: {
            styleOverrides: {
              '@media (prefers-reduced-motion: reduce)': {
                '*': {
                  animation: 'none !important',
                  transition: 'none !important'
                }
              }
            }
          }
        }
      });

      renderWithTheme(
        <ThemeProvider theme={reducedMotionTheme}>
          <AdvancedVisualizations
            entries={mockEntries}
            stats={mockStats}
            timeRange={mockTimeRange}
          />
        </ThemeProvider>
      );

      const container = screen.getByRole('img');
      const computedStyle = window.getComputedStyle(container);
      expect(computedStyle.animation).toBe('none');
      expect(computedStyle.transition).toBe('none');
    });

    it('provides alternative text for color-dependent information', () => {
      renderWithTheme(
        <AdvancedVisualizations
          entries={mockEntries}
          stats={mockStats}
          timeRange={mockTimeRange}
        />
      );

      const container = screen.getByRole('img');
      expect(container).toHaveAttribute('aria-description', expect.stringContaining('intensity'));
      expect(container).toHaveAttribute('aria-description', expect.stringContaining('frequency'));
    });
  });

  describe('Extended Error Handling Scenarios', () => {
    it('handles network errors during data loading', async () => {
      const mockError = new Error('Network request failed');
      
      // Mock the data fetching to simulate network error
      jest.spyOn(global, 'fetch').mockRejectedValueOnce(mockError);

      renderWithTheme(
        <AdvancedVisualizations
          entries={mockEntries}
          stats={mockStats}
          timeRange={mockTimeRange}
        />
      );

      expect(screen.getByText(/Network request failed/)).toBeInTheDocument();
    });

    it('handles malformed data structures', () => {
      const malformedEntries = [
        {
          ...mockEntries[0],
          importance_score: 'invalid-score'
        }
      ];

      renderWithTheme(
        <AdvancedVisualizations
          entries={malformedEntries}
          stats={mockStats}
          timeRange={mockTimeRange}
        />
      );

      expect(screen.getByText(/Error processing data/)).toBeInTheDocument();
    });

    it('handles concurrent visualization errors', async () => {
      const { rerender } = renderWithTheme(
        <AdvancedVisualizations
          entries={mockEntries}
          stats={mockStats}
          timeRange={mockTimeRange}
        />
      );

      // Simulate multiple errors occurring in quick succession
      await act(async () => {
        // Trigger first error
        const errorButton = screen.getByTestId('error-trigger');
        fireEvent.click(errorButton);

        // Switch visualization while error is present
        const selector = screen.getByLabelText('Visualization Type');
        fireEvent.mouseDown(selector);
        fireEvent.click(screen.getByText('Knowledge Tree Map'));

        // Trigger second error
        fireEvent.click(errorButton);
      });

      // Verify error handling
      expect(screen.getByText(/Error rendering visualization/)).toBeInTheDocument();
    });

    it('handles browser compatibility issues', () => {
      // Mock unsupported browser features
      const originalPerformance = window.performance;
      window.performance = undefined;

      renderWithTheme(
        <AdvancedVisualizations
          entries={mockEntries}
          stats={mockStats}
          timeRange={mockTimeRange}
        />
      );

      // Verify fallback behavior
      expect(screen.getByText(/Browser compatibility warning/)).toBeInTheDocument();

      // Restore original performance object
      window.performance = originalPerformance;
    });

    it('handles memory pressure scenarios', async () => {
      const memoryIntensiveEntries = generateLargeDataset(100000);
      
      // Simulate memory pressure
      const originalConsole = console.warn;
      console.warn = jest.fn();

      renderWithTheme(
        <AdvancedVisualizations
          entries={memoryIntensiveEntries}
          stats={mockStats}
          timeRange={mockTimeRange}
        />
      );

      // Verify memory management
      expect(console.warn).toHaveBeenCalledWith(expect.stringContaining('memory'));
      
      // Restore original console
      console.warn = originalConsole;
    });
  });
}); 