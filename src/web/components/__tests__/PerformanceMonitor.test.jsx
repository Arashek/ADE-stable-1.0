import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { ThemeProvider, createTheme } from '@mui/material';
import PerformanceMonitor from '../PerformanceMonitor';
import performanceMonitor from '../../utils/performance-monitor';

// Mock the performance monitor
jest.mock('../../utils/performance-monitor', () => ({
  __esModule: true,
  default: {
    getReport: jest.fn(),
    exportData: jest.fn()
  }
}));

const theme = createTheme();

const mockReport = {
  timings: {
    testOperation: {
      count: 2,
      average: 150,
      max: 200,
      min: 100,
      p95: 180,
      p99: 190
    }
  },
  memory: {
    averageUsed: 50 * 1024 * 1024,
    averageTotal: 100 * 1024 * 1024,
    maxUsed: 60 * 1024 * 1024,
    maxTotal: 120 * 1024 * 1024
  },
  interactions: {
    buttonClick: {
      count: 3,
      average: 75,
      max: 100,
      min: 50
    }
  },
  network: {
    resources: {
      script: {
        count: 2,
        averageDuration: 150,
        totalSize: 2048,
        maxDuration: 200,
        minDuration: 100
      },
      image: {
        count: 3,
        averageDuration: 80,
        totalSize: 3072,
        maxDuration: 100,
        minDuration: 60
      }
    },
    navigation: {
      count: 1,
      averageLoadTime: 2000,
      averageDomContentLoaded: 1500,
      averageFirstPaint: 1000,
      averageFirstContentfulPaint: 1200,
      maxLoadTime: 2000,
      minLoadTime: 2000
    },
    connection: {
      count: 1,
      types: { wifi: 1 },
      effectiveTypes: { '4g': 1 },
      averageRtt: 50,
      averageDownlink: 10,
      maxRtt: 50,
      minRtt: 50,
      maxDownlink: 10,
      minDownlink: 10
    }
  },
  errors: [
    { message: 'Test error 1' },
    { message: 'Test error 2' }
  ]
};

const renderWithTheme = (component) => {
  return render(
    <ThemeProvider theme={theme}>
      {component}
    </ThemeProvider>
  );
};

describe('PerformanceMonitor', () => {
  beforeEach(() => {
    performanceMonitor.getReport.mockResolvedValue(mockReport);
  });

  it('renders without crashing', () => {
    renderWithTheme(<PerformanceMonitor />);
    expect(screen.getByText('Performance Monitor')).toBeInTheDocument();
  });

  it('displays timing statistics', async () => {
    renderWithTheme(<PerformanceMonitor />);
    
    await waitFor(() => {
      expect(screen.getByText('testOperation')).toBeInTheDocument();
      expect(screen.getByText('Average: 150.00ms')).toBeInTheDocument();
      expect(screen.getByText('P95: 180.00ms')).toBeInTheDocument();
      expect(screen.getByText('P99: 190.00ms')).toBeInTheDocument();
    });
  });

  it('displays memory statistics', async () => {
    renderWithTheme(<PerformanceMonitor />);
    
    await waitFor(() => {
      expect(screen.getByText('Memory Usage')).toBeInTheDocument();
      expect(screen.getByText('Average Used: 50.00 MB')).toBeInTheDocument();
      expect(screen.getByText('Average Total: 100.00 MB')).toBeInTheDocument();
      expect(screen.getByText('Max Used: 60.00 MB')).toBeInTheDocument();
      expect(screen.getByText('Max Total: 120.00 MB')).toBeInTheDocument();
    });
  });

  it('displays interaction statistics', async () => {
    renderWithTheme(<PerformanceMonitor />);
    
    await waitFor(() => {
      expect(screen.getByText('buttonClick')).toBeInTheDocument();
      expect(screen.getByText('Count: 3')).toBeInTheDocument();
      expect(screen.getByText('Average: 75.00ms')).toBeInTheDocument();
      expect(screen.getByText('Max: 100.00ms')).toBeInTheDocument();
      expect(screen.getByText('Min: 50.00ms')).toBeInTheDocument();
    });
  });

  it('displays errors', async () => {
    renderWithTheme(<PerformanceMonitor />);
    
    await waitFor(() => {
      expect(screen.getByText('Test error 1')).toBeInTheDocument();
      expect(screen.getByText('Test error 2')).toBeInTheDocument();
    });
  });

  it('refreshes data when refresh button is clicked', async () => {
    renderWithTheme(<PerformanceMonitor />);
    
    const refreshButton = screen.getByTitle('Refresh');
    fireEvent.click(refreshButton);
    
    await waitFor(() => {
      expect(performanceMonitor.getReport).toHaveBeenCalledTimes(2);
    });
  });

  it('exports data when export button is clicked', async () => {
    renderWithTheme(<PerformanceMonitor />);
    
    const exportButton = screen.getByTitle('Export Data');
    fireEvent.click(exportButton);
    
    expect(performanceMonitor.exportData).toHaveBeenCalled();
  });

  it('toggles expansion when expand/collapse button is clicked', async () => {
    renderWithTheme(<PerformanceMonitor />);
    
    const expandButton = screen.getByRole('button', { name: /expand/i });
    fireEvent.click(expandButton);
    
    await waitFor(() => {
      expect(screen.queryByText('Memory Usage')).not.toBeInTheDocument();
    });
    
    fireEvent.click(expandButton);
    
    await waitFor(() => {
      expect(screen.getByText('Memory Usage')).toBeInTheDocument();
    });
  });

  it('displays error message when report fetch fails', async () => {
    const error = new Error('Failed to fetch report');
    performanceMonitor.getReport.mockRejectedValue(error);
    
    renderWithTheme(<PerformanceMonitor />);
    
    await waitFor(() => {
      expect(screen.getByText('Failed to fetch report')).toBeInTheDocument();
    });
  });

  it('updates data periodically', async () => {
    jest.useFakeTimers();
    
    renderWithTheme(<PerformanceMonitor />);
    
    await waitFor(() => {
      expect(performanceMonitor.getReport).toHaveBeenCalledTimes(1);
    });
    
    jest.advanceTimersByTime(30000); // Advance 30 seconds
    
    await waitFor(() => {
      expect(performanceMonitor.getReport).toHaveBeenCalledTimes(2);
    });
    
    jest.useRealTimers();
  });

  describe('Network Performance Visualizations', () => {
    it('displays network performance section', async () => {
      renderWithTheme(<PerformanceMonitor />);
      
      await waitFor(() => {
        expect(screen.getByText('Network Performance')).toBeInTheDocument();
      });
    });

    it('displays page load performance metrics', async () => {
      renderWithTheme(<PerformanceMonitor />);
      
      await waitFor(() => {
        expect(screen.getByText('Page Load Performance')).toBeInTheDocument();
        expect(screen.getByText('Average Load Time: 2000.00ms')).toBeInTheDocument();
        expect(screen.getByText('DOM Content Loaded: 1500.00ms')).toBeInTheDocument();
        expect(screen.getByText('First Paint: 1000.00ms')).toBeInTheDocument();
        expect(screen.getByText('First Contentful Paint: 1200.00ms')).toBeInTheDocument();
      });
    });

    it('displays resource loading table', async () => {
      renderWithTheme(<PerformanceMonitor />);
      
      await waitFor(() => {
        expect(screen.getByText('Resource Loading')).toBeInTheDocument();
        expect(screen.getByText('script')).toBeInTheDocument();
        expect(screen.getByText('image')).toBeInTheDocument();
        expect(screen.getByText('2')).toBeInTheDocument(); // script count
        expect(screen.getByText('3')).toBeInTheDocument(); // image count
        expect(screen.getByText('150.00ms')).toBeInTheDocument(); // script avg duration
        expect(screen.getByText('80.00ms')).toBeInTheDocument(); // image avg duration
        expect(screen.getByText('2.00KB')).toBeInTheDocument(); // script total size
        expect(screen.getByText('3.00KB')).toBeInTheDocument(); // image total size
      });
    });

    it('displays connection information', async () => {
      renderWithTheme(<PerformanceMonitor />);
      
      await waitFor(() => {
        expect(screen.getByText('Connection Information')).toBeInTheDocument();
        expect(screen.getByText('Type: wifi (1)')).toBeInTheDocument();
        expect(screen.getByText('Effective Type: 4g (1)')).toBeInTheDocument();
        expect(screen.getByText('Average RTT: 50.00ms')).toBeInTheDocument();
        expect(screen.getByText('Average Downlink: 10.00Mbps')).toBeInTheDocument();
      });
    });

    it('displays connection quality indicators', async () => {
      renderWithTheme(<PerformanceMonitor />);
      
      await waitFor(() => {
        expect(screen.getByText('RTT Quality')).toBeInTheDocument();
        expect(screen.getByText('Downlink Speed')).toBeInTheDocument();
        
        // Check for progress bars
        const progressBars = screen.getAllByRole('progressbar');
        expect(progressBars).toHaveLength(2);
      });
    });

    it('updates network metrics on refresh', async () => {
      renderWithTheme(<PerformanceMonitor />);
      
      const refreshButton = screen.getByTitle('Refresh');
      fireEvent.click(refreshButton);
      
      await waitFor(() => {
        expect(performanceMonitor.getReport).toHaveBeenCalledTimes(2);
      });
    });

    it('handles missing network data gracefully', async () => {
      const reportWithoutNetwork = {
        ...mockReport,
        network: null
      };
      performanceMonitor.getReport.mockResolvedValue(reportWithoutNetwork);
      
      renderWithTheme(<PerformanceMonitor />);
      
      await waitFor(() => {
        expect(screen.queryByText('Network Performance')).not.toBeInTheDocument();
      });
    });

    it('handles partial network data gracefully', async () => {
      const reportWithPartialNetwork = {
        ...mockReport,
        network: {
          resources: null,
          navigation: mockReport.network.navigation,
          connection: null
        }
      };
      performanceMonitor.getReport.mockResolvedValue(reportWithPartialNetwork);
      
      renderWithTheme(<PerformanceMonitor />);
      
      await waitFor(() => {
        expect(screen.getByText('Network Performance')).toBeInTheDocument();
        expect(screen.getByText('Page Load Performance')).toBeInTheDocument();
        expect(screen.queryByText('Resource Loading')).not.toBeInTheDocument();
        expect(screen.queryByText('Connection Information')).not.toBeInTheDocument();
      });
    });
  });
}); 