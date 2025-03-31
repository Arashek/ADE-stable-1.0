import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { ThemeProvider } from '@mui/material';
import { createTheme } from '@mui/material/styles';
import CommandCenter from '../CommandCenter';
import { GlobalProvider } from '../../state/GlobalContext';
import useFeatureFlags from '../../utils/feature-flags';

// Mock feature flags
jest.mock('../../utils/feature-flags');

// Create test theme
const theme = createTheme();

// Test wrapper component
const TestWrapper = ({ children }) => (
  <ThemeProvider theme={theme}>
    <GlobalProvider>
      {children}
    </GlobalProvider>
  </ThemeProvider>
);

describe('CommandCenter', () => {
  beforeEach(() => {
    // Reset feature flags mock
    useFeatureFlags.mockImplementation(() => ({
      isFeatureEnabled: () => true,
      getFeatureVariant: () => 'control',
      trackFeatureUsage: jest.fn()
    }));
  });

  // Unit Tests
  describe('Rendering', () => {
    it('renders without crashing', () => {
      render(<CommandCenter />, { wrapper: TestWrapper });
      expect(screen.getByText('Command Center')).toBeInTheDocument();
    });

    it('displays toggle button', () => {
      render(<CommandCenter />, { wrapper: TestWrapper });
      expect(screen.getByRole('button')).toBeInTheDocument();
    });

    it('applies correct theme styles', () => {
      render(<CommandCenter />, { wrapper: TestWrapper });
      const paper = screen.getByRole('presentation');
      expect(paper).toHaveStyle({
        position: 'fixed',
        width: '400px',
        height: '100vh'
      });
    });
  });

  // Integration Tests
  describe('Interactions', () => {
    it('toggles visibility on button click', async () => {
      render(<CommandCenter />, { wrapper: TestWrapper });
      const toggleButton = screen.getByRole('button');
      
      // Initially closed
      expect(screen.getByRole('presentation')).toHaveStyle({
        transform: expect.stringContaining('-100%')
      });

      // Open
      fireEvent.click(toggleButton);
      await waitFor(() => {
        expect(screen.getByRole('presentation')).toHaveStyle({
          transform: 'translateX(0)'
        });
      });

      // Close
      fireEvent.click(toggleButton);
      await waitFor(() => {
        expect(screen.getByRole('presentation')).toHaveStyle({
          transform: expect.stringContaining('-100%')
        });
      });
    });

    it('switches position when position toggle is clicked', async () => {
      render(<CommandCenter />, { wrapper: TestWrapper });
      
      // Open panel
      fireEvent.click(screen.getByRole('button'));
      
      // Find and click position toggle
      const positionToggle = screen.getByLabelText('toggle position');
      fireEvent.click(positionToggle);
      
      await waitFor(() => {
        expect(screen.getByRole('presentation')).toHaveStyle({
          left: '0'
        });
      });
    });

    it('auto-opens on errors when enabled', async () => {
      const { rerender } = render(<CommandCenter />, { wrapper: TestWrapper });
      
      // Simulate error state
      const mockDispatch = jest.fn();
      jest.spyOn(require('../../state/GlobalContext'), 'useGlobal').mockImplementation(() => ({
        state: {
          errors: [{ message: 'Test error' }],
          userPreferences: { autoOpenOnError: true }
        },
        dispatch: mockDispatch
      }));
      
      rerender(<CommandCenter />);
      
      await waitFor(() => {
        expect(mockDispatch).toHaveBeenCalledWith({
          type: 'TOGGLE_COMMAND_CENTER',
          payload: true
        });
      });
    });
  });

  // Performance Tests
  describe('Performance', () => {
    it('maintains smooth transitions', async () => {
      render(<CommandCenter />, { wrapper: TestWrapper });
      
      const startTime = performance.now();
      fireEvent.click(screen.getByRole('button'));
      
      await waitFor(() => {
        const endTime = performance.now();
        expect(endTime - startTime).toBeLessThan(300); // Should complete within 300ms
      });
    });

    it('handles rapid state changes without lag', async () => {
      render(<CommandCenter />, { wrapper: TestWrapper });
      
      const toggleButton = screen.getByRole('button');
      const startTime = performance.now();
      
      // Simulate rapid toggling
      for (let i = 0; i < 5; i++) {
        fireEvent.click(toggleButton);
        await new Promise(resolve => setTimeout(resolve, 50));
      }
      
      const endTime = performance.now();
      expect(endTime - startTime).toBeLessThan(1000); // Should complete within 1s
    });
  });

  // Accessibility Tests
  describe('Accessibility', () => {
    it('maintains keyboard navigation', () => {
      render(<CommandCenter />, { wrapper: TestWrapper });
      
      // Tab to toggle button
      fireEvent.keyDown(document.body, { key: 'Tab', code: 'Tab' });
      expect(screen.getByRole('button')).toHaveFocus();
      
      // Toggle with Enter
      fireEvent.keyDown(screen.getByRole('button'), { key: 'Enter', code: 'Enter' });
      expect(screen.getByRole('presentation')).toHaveStyle({
        transform: 'translateX(0)'
      });
    });

    it('provides appropriate ARIA labels', () => {
      render(<CommandCenter />, { wrapper: TestWrapper });
      
      expect(screen.getByRole('button')).toHaveAttribute('aria-label', 'Toggle Command Center');
      expect(screen.getByRole('presentation')).toHaveAttribute('aria-label', 'Command Center Panel');
    });

    it('maintains focus management', async () => {
      render(<CommandCenter />, { wrapper: TestWrapper });
      
      // Open panel
      fireEvent.click(screen.getByRole('button'));
      
      // Focus should be trapped within panel
      const closeButton = screen.getByLabelText('Close Command Center');
      fireEvent.keyDown(closeButton, { key: 'Tab', code: 'Tab', shiftKey: true });
      
      await waitFor(() => {
        expect(screen.getByLabelText('Toggle Command Center')).toHaveFocus();
      });
    });
  });

  // Error Handling Tests
  describe('Error Handling', () => {
    it('handles feature flag errors gracefully', () => {
      useFeatureFlags.mockImplementation(() => {
        throw new Error('Feature flag error');
      });
      
      const consoleSpy = jest.spyOn(console, 'error').mockImplementation(() => {});
      render(<CommandCenter />, { wrapper: TestWrapper });
      
      expect(consoleSpy).toHaveBeenCalled();
      expect(screen.getByText('Command Center')).toBeInTheDocument();
      
      consoleSpy.mockRestore();
    });

    it('recovers from state management errors', async () => {
      const mockDispatch = jest.fn().mockRejectedValue(new Error('State error'));
      jest.spyOn(require('../../state/GlobalContext'), 'useGlobal').mockImplementation(() => ({
        state: { isCommandCenterOpen: false },
        dispatch: mockDispatch
      }));
      
      const consoleSpy = jest.spyOn(console, 'error').mockImplementation(() => {});
      render(<CommandCenter />, { wrapper: TestWrapper });
      
      fireEvent.click(screen.getByRole('button'));
      
      await waitFor(() => {
        expect(consoleSpy).toHaveBeenCalled();
        expect(screen.getByRole('presentation')).toBeInTheDocument();
      });
      
      consoleSpy.mockRestore();
    });
  });
}); 