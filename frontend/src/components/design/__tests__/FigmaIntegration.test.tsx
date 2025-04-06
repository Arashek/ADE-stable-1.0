import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { FigmaIntegration } from '../FigmaIntegration';

describe('FigmaIntegration', () => {
  const mockOnFileSelect = jest.fn();
  const mockOnComponentSelect = jest.fn();
  const mockOnStyleSelect = jest.fn();
  const mockOnDesignUpdate = jest.fn();
  const mockOnFinalize = jest.fn();
  const mockDesignAgent = {
    validateDesign: jest.fn(),
    generateImplementation: jest.fn()
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders the simplified design integration component', () => {
    render(
      <FigmaIntegration
        onFileSelect={mockOnFileSelect}
        onComponentSelect={mockOnComponentSelect}
        onStyleSelect={mockOnStyleSelect}
        onDesignUpdate={mockOnDesignUpdate}
        onFinalize={mockOnFinalize}
        designAgent={mockDesignAgent}
      />
    );

    expect(screen.getByText('Design System Integration')).toBeInTheDocument();
    expect(screen.getByText(/External design integrations have been simplified/)).toBeInTheDocument();
    expect(screen.getByLabelText('Design System Name')).toBeInTheDocument();
    expect(screen.getByText('Create Basic Design System')).toBeInTheDocument();
  });

  it('creates a basic design system when button is clicked', async () => {
    render(
      <FigmaIntegration
        onFileSelect={mockOnFileSelect}
        onComponentSelect={mockOnComponentSelect}
        onStyleSelect={mockOnStyleSelect}
        onDesignUpdate={mockOnDesignUpdate}
        onFinalize={mockOnFinalize}
        designAgent={mockDesignAgent}
      />
    );

    // Enter a design name
    fireEvent.change(screen.getByLabelText('Design System Name'), {
      target: { value: 'Test Design System' }
    });

    // Click the create button
    fireEvent.click(screen.getByText('Create Basic Design System'));

    // Wait for the async operation to complete
    await waitFor(() => {
      expect(mockOnFinalize).toHaveBeenCalled();
    });

    // Verify the design system structure
    const designSystem = mockOnFinalize.mock.calls[0][0];
    expect(designSystem).toHaveProperty('name', 'Test Design System');
    expect(designSystem).toHaveProperty('components');
    expect(designSystem).toHaveProperty('styles');
    expect(designSystem).toHaveProperty('metadata');
  });
});