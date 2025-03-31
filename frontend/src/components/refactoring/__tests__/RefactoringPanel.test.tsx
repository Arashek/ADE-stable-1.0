import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import RefactoringPanel from '../RefactoringPanel';
import { RefactoringOperation } from '../../../types/refactoring';

describe('RefactoringPanel', () => {
  const mockOnApplyRefactoring = jest.fn();
  const mockOnPreviewRefactoring = jest.fn();
  const mockOnUndo = jest.fn();
  const mockOnRedo = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('should render the panel with available refactoring options', () => {
    render(
      <RefactoringPanel
        onApplyRefactoring={mockOnApplyRefactoring}
        onPreviewRefactoring={mockOnPreviewRefactoring}
        onUndo={mockOnUndo}
        onRedo={mockOnRedo}
      />
    );

    // Check if all refactoring options are rendered
    expect(screen.getByText('Extract Method')).toBeInTheDocument();
    expect(screen.getByText('Rename Symbol')).toBeInTheDocument();
    expect(screen.getByText('Extract Variable')).toBeInTheDocument();
    expect(screen.getByText('Inline Variable')).toBeInTheDocument();
    expect(screen.getByText('Move Method')).toBeInTheDocument();
    expect(screen.getByText('Change Signature')).toBeInTheDocument();
  });

  it('should show refactoring details when an option is selected', () => {
    render(
      <RefactoringPanel
        onApplyRefactoring={mockOnApplyRefactoring}
        onPreviewRefactoring={mockOnPreviewRefactoring}
        onUndo={mockOnUndo}
        onRedo={mockOnRedo}
      />
    );

    // Click on Extract Method option
    fireEvent.click(screen.getByText('Extract Method'));

    // Check if details are shown
    expect(screen.getByText('Refactoring Details')).toBeInTheDocument();
    expect(screen.getByText('Description')).toBeInTheDocument();
    expect(screen.getByText('File')).toBeInTheDocument();
    expect(screen.getByText('Line')).toBeInTheDocument();
  });

  it('should handle preview action', async () => {
    render(
      <RefactoringPanel
        onApplyRefactoring={mockOnApplyRefactoring}
        onPreviewRefactoring={mockOnPreviewRefactoring}
        onUndo={mockOnUndo}
        onRedo={mockOnRedo}
      />
    );

    // Click on Extract Method option
    fireEvent.click(screen.getByText('Extract Method'));

    // Click Preview button
    fireEvent.click(screen.getByText('Preview'));

    // Check if preview function was called
    await waitFor(() => {
      expect(mockOnPreviewRefactoring).toHaveBeenCalled();
    });
  });

  it('should handle apply action', async () => {
    render(
      <RefactoringPanel
        onApplyRefactoring={mockOnApplyRefactoring}
        onPreviewRefactoring={mockOnPreviewRefactoring}
        onUndo={mockOnUndo}
        onRedo={mockOnRedo}
      />
    );

    // Click on Extract Method option
    fireEvent.click(screen.getByText('Extract Method'));

    // Click Apply button
    fireEvent.click(screen.getByText('Apply'));

    // Check if apply function was called
    await waitFor(() => {
      expect(mockOnApplyRefactoring).toHaveBeenCalled();
    });
  });

  it('should handle undo and redo actions', () => {
    render(
      <RefactoringPanel
        onApplyRefactoring={mockOnApplyRefactoring}
        onPreviewRefactoring={mockOnPreviewRefactoring}
        onUndo={mockOnUndo}
        onRedo={mockOnRedo}
      />
    );

    // Click undo button
    fireEvent.click(screen.getByTitle('Undo'));
    expect(mockOnUndo).toHaveBeenCalled();

    // Click redo button
    fireEvent.click(screen.getByTitle('Redo'));
    expect(mockOnRedo).toHaveBeenCalled();
  });

  it('should show error message when refactoring fails', async () => {
    const error = new Error('Refactoring failed');
    mockOnApplyRefactoring.mockRejectedValue(error);

    render(
      <RefactoringPanel
        onApplyRefactoring={mockOnApplyRefactoring}
        onPreviewRefactoring={mockOnPreviewRefactoring}
        onUndo={mockOnUndo}
        onRedo={mockOnRedo}
      />
    );

    // Click on Extract Method option
    fireEvent.click(screen.getByText('Extract Method'));

    // Click Apply button
    fireEvent.click(screen.getByText('Apply'));

    // Check if error message is shown
    await waitFor(() => {
      expect(screen.getByText('Refactoring failed')).toBeInTheDocument();
    });
  });

  it('should show preview content when available', async () => {
    const previewContent = '// Preview of refactored code';
    mockOnPreviewRefactoring.mockResolvedValue(previewContent);

    render(
      <RefactoringPanel
        onApplyRefactoring={mockOnApplyRefactoring}
        onPreviewRefactoring={mockOnPreviewRefactoring}
        onUndo={mockOnUndo}
        onRedo={mockOnRedo}
      />
    );

    // Click on Extract Method option
    fireEvent.click(screen.getByText('Extract Method'));

    // Click Preview button
    fireEvent.click(screen.getByText('Preview'));

    // Check if preview content is shown
    await waitFor(() => {
      expect(screen.getByText(previewContent)).toBeInTheDocument();
    });
  });

  it('should show operation history', async () => {
    const operation: RefactoringOperation = {
      id: '1',
      type: 'extract-method',
      description: 'Test operation',
      file: 'test.ts',
      line: 1,
      status: 'applied'
    };

    mockOnApplyRefactoring.mockResolvedValue(undefined);

    render(
      <RefactoringPanel
        onApplyRefactoring={mockOnApplyRefactoring}
        onPreviewRefactoring={mockOnPreviewRefactoring}
        onUndo={mockOnUndo}
        onRedo={mockOnRedo}
      />
    );

    // Click on Extract Method option
    fireEvent.click(screen.getByText('Extract Method'));

    // Click Apply button
    fireEvent.click(screen.getByText('Apply'));

    // Check if operation appears in history
    await waitFor(() => {
      expect(screen.getByText('Test operation')).toBeInTheDocument();
    });

    await waitFor(() => {
      expect(screen.getByText('test.ts:1')).toBeInTheDocument();
    });
  });
}); 