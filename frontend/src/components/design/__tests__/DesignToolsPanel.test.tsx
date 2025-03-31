import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { DesignToolsPanel } from '../DesignToolsPanel';
import { DesignTool } from '../../../../backend/src/services/design/DesignToolService';

// Mock the DesignToolService
jest.mock('../../../../backend/src/services/design/DesignToolService', () => ({
  DesignToolService: jest.fn().mockImplementation(() => ({
    getAllTools: () => [
      {
        id: 'rectangle',
        name: 'Rectangle',
        type: 'shape',
        icon: 'rectangle',
        description: 'Draw a rectangle shape',
        properties: [
          {
            id: 'fill',
            name: 'fill',
            type: 'color',
            label: 'Fill Color',
            defaultValue: '#ffffff',
          },
          {
            id: 'strokeWidth',
            name: 'strokeWidth',
            type: 'number',
            label: 'Stroke Width',
            defaultValue: 2,
            min: 0,
            max: 20,
            step: 1,
          },
        ],
      },
      {
        id: 'text',
        name: 'Text',
        type: 'text',
        icon: 'text',
        description: 'Add text to the canvas',
        properties: [
          {
            id: 'fontFamily',
            name: 'fontFamily',
            type: 'select',
            label: 'Font Family',
            defaultValue: 'Arial',
            options: [
              { label: 'Arial', value: 'Arial' },
              { label: 'Times New Roman', value: 'Times New Roman' },
            ],
          },
        ],
      },
    ],
  })),
}));

describe('DesignToolsPanel', () => {
  const mockOnToolSelect = jest.fn();
  const mockOnPropertyChange = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders the tools panel with search and tabs', () => {
    render(
      <DesignToolsPanel
        onToolSelect={mockOnToolSelect}
        onPropertyChange={mockOnPropertyChange}
      />
    );

    // Check if search input is rendered
    expect(screen.getByPlaceholderText('Search tools...')).toBeInTheDocument();

    // Check if tool type tabs are rendered
    expect(screen.getByText('all')).toBeInTheDocument();
    expect(screen.getByText('shape')).toBeInTheDocument();
    expect(screen.getByText('text')).toBeInTheDocument();
    expect(screen.getByText('media')).toBeInTheDocument();
    expect(screen.getByText('data')).toBeInTheDocument();
    expect(screen.getByText('interactive')).toBeInTheDocument();

    // Check if tools are rendered
    expect(screen.getByText('Rectangle')).toBeInTheDocument();
    expect(screen.getByText('Text')).toBeInTheDocument();
  });

  it('filters tools based on search query', async () => {
    render(
      <DesignToolsPanel
        onToolSelect={mockOnToolSelect}
        onPropertyChange={mockOnPropertyChange}
      />
    );

    const searchInput = screen.getByPlaceholderText('Search tools...');
    fireEvent.change(searchInput, { target: { value: 'rectangle' } });

    await waitFor(() => {
      expect(screen.getByText('Rectangle')).toBeInTheDocument();
      expect(screen.queryByText('Text')).not.toBeInTheDocument();
    });
  });

  it('filters tools based on selected tab', async () => {
    render(
      <DesignToolsPanel
        onToolSelect={mockOnToolSelect}
        onPropertyChange={mockOnPropertyChange}
      />
    );

    const shapeTab = screen.getByText('shape');
    fireEvent.click(shapeTab);

    await waitFor(() => {
      expect(screen.getByText('Rectangle')).toBeInTheDocument();
      expect(screen.queryByText('Text')).not.toBeInTheDocument();
    });
  });

  it('calls onToolSelect when a tool is clicked', () => {
    render(
      <DesignToolsPanel
        onToolSelect={mockOnToolSelect}
        onPropertyChange={mockOnPropertyChange}
      />
    );

    const rectangleTool = screen.getByText('Rectangle');
    fireEvent.click(rectangleTool);

    expect(mockOnToolSelect).toHaveBeenCalledWith(
      expect.objectContaining({
        id: 'rectangle',
        name: 'Rectangle',
        type: 'shape',
      })
    );
  });

  it('renders property editors for selected tool', () => {
    const selectedTool: DesignTool = {
      id: 'rectangle',
      name: 'Rectangle',
      type: 'shape',
      icon: 'rectangle',
      description: 'Draw a rectangle shape',
      properties: [
        {
          id: 'fill',
          name: 'fill',
          type: 'color',
          label: 'Fill Color',
          defaultValue: '#ffffff',
        },
        {
          id: 'strokeWidth',
          name: 'strokeWidth',
          type: 'number',
          label: 'Stroke Width',
          defaultValue: 2,
          min: 0,
          max: 20,
          step: 1,
        },
      ],
    };

    render(
      <DesignToolsPanel
        onToolSelect={mockOnToolSelect}
        onPropertyChange={mockOnPropertyChange}
        selectedTool={selectedTool}
      />
    );

    // Check if property editors are rendered
    expect(screen.getByLabelText('Fill Color')).toBeInTheDocument();
    expect(screen.getByLabelText('Stroke Width')).toBeInTheDocument();
  });

  it('calls onPropertyChange when a property is modified', () => {
    const selectedTool: DesignTool = {
      id: 'rectangle',
      name: 'Rectangle',
      type: 'shape',
      icon: 'rectangle',
      description: 'Draw a rectangle shape',
      properties: [
        {
          id: 'fill',
          name: 'fill',
          type: 'color',
          label: 'Fill Color',
          defaultValue: '#ffffff',
        },
      ],
    };

    render(
      <DesignToolsPanel
        onToolSelect={mockOnToolSelect}
        onPropertyChange={mockOnPropertyChange}
        selectedTool={selectedTool}
      />
    );

    const colorInput = screen.getByLabelText('Fill Color');
    fireEvent.change(colorInput, { target: { value: '#000000' } });

    expect(mockOnPropertyChange).toHaveBeenCalledWith(
      'rectangle',
      'fill',
      '#000000'
    );
  });

  it('renders different property editor types correctly', () => {
    const selectedTool: DesignTool = {
      id: 'test-tool',
      name: 'Test Tool',
      type: 'test',
      icon: 'test',
      description: 'Test tool with various properties',
      properties: [
        {
          id: 'color',
          name: 'color',
          type: 'color',
          label: 'Color',
          defaultValue: '#ffffff',
        },
        {
          id: 'number',
          name: 'number',
          type: 'number',
          label: 'Number',
          defaultValue: 5,
          min: 0,
          max: 10,
          step: 1,
        },
        {
          id: 'boolean',
          name: 'boolean',
          type: 'boolean',
          label: 'Boolean',
          defaultValue: false,
        },
        {
          id: 'select',
          name: 'select',
          type: 'select',
          label: 'Select',
          defaultValue: 'option1',
          options: [
            { label: 'Option 1', value: 'option1' },
            { label: 'Option 2', value: 'option2' },
          ],
        },
        {
          id: 'slider',
          name: 'slider',
          type: 'slider',
          label: 'Slider',
          defaultValue: 0.5,
          min: 0,
          max: 1,
          step: 0.1,
        },
      ],
    };

    render(
      <DesignToolsPanel
        onToolSelect={mockOnToolSelect}
        onPropertyChange={mockOnPropertyChange}
        selectedTool={selectedTool}
      />
    );

    // Check if all property editor types are rendered
    expect(screen.getByLabelText('Color')).toBeInTheDocument();
    expect(screen.getByLabelText('Number')).toBeInTheDocument();
    expect(screen.getByLabelText('Boolean')).toBeInTheDocument();
    expect(screen.getByLabelText('Select')).toBeInTheDocument();
    expect(screen.getByLabelText('Slider')).toBeInTheDocument();
  });
}); 