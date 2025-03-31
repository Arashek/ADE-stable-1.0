import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BackupDashboard } from '../../../components/backup/BackupDashboard';
import { BackupMetadata } from '../../../core/backup/BackupManager';

describe('BackupDashboard', () => {
  const mockBackups: BackupMetadata[] = [
    {
      id: 'backup-1',
      timestamp: new Date(),
      type: 'container',
      status: 'completed',
      size: 1024 * 1024, // 1MB
      checksum: 'test-checksum-1',
      tags: ['test', 'production']
    },
    {
      id: 'backup-2',
      timestamp: new Date(),
      type: 'project',
      status: 'in_progress',
      size: 2048 * 1024, // 2MB
      checksum: 'test-checksum-2',
      tags: ['development']
    }
  ];

  const mockProps = {
    onRefresh: jest.fn(),
    onBackup: jest.fn(),
    onRestore: jest.fn(),
    onDelete: jest.fn(),
    backups: mockBackups,
    activeBackups: ['backup-2'],
    activeRestores: [],
    error: undefined
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders backup statistics correctly', () => {
    render(<BackupDashboard {...mockProps} />);

    expect(screen.getByText('Total Backups')).toBeInTheDocument();
    expect(screen.getByText('2')).toBeInTheDocument();
    expect(screen.getByText('Active Backups')).toBeInTheDocument();
    expect(screen.getByText('1')).toBeInTheDocument();
    expect(screen.getByText('Active Restores')).toBeInTheDocument();
    expect(screen.getByText('0')).toBeInTheDocument();
  });

  it('renders backup table with correct data', () => {
    render(<BackupDashboard {...mockProps} />);

    // Check table headers
    expect(screen.getByText('ID')).toBeInTheDocument();
    expect(screen.getByText('Type')).toBeInTheDocument();
    expect(screen.getByText('Status')).toBeInTheDocument();
    expect(screen.getByText('Size')).toBeInTheDocument();
    expect(screen.getByText('Created')).toBeInTheDocument();
    expect(screen.getByText('Tags')).toBeInTheDocument();
    expect(screen.getByText('Actions')).toBeInTheDocument();

    // Check backup data
    expect(screen.getByText('backup-1')).toBeInTheDocument();
    expect(screen.getByText('container')).toBeInTheDocument();
    expect(screen.getByText('completed')).toBeInTheDocument();
    expect(screen.getByText('1.00 MB')).toBeInTheDocument();
    expect(screen.getByText('test')).toBeInTheDocument();
    expect(screen.getByText('production')).toBeInTheDocument();
  });

  it('handles refresh button click', async () => {
    render(<BackupDashboard {...mockProps} />);

    const refreshButton = screen.getByText('Refresh');
    fireEvent.click(refreshButton);

    await waitFor(() => {
      expect(mockProps.onRefresh).toHaveBeenCalledTimes(1);
    });
  });

  it('opens backup dialog when create backup button is clicked', () => {
    render(<BackupDashboard {...mockProps} />);

    const createButton = screen.getByText('Create Backup');
    fireEvent.click(createButton);

    expect(screen.getByText('Create Backup')).toBeInTheDocument();
    expect(screen.getByLabelText('Backup Type')).toBeInTheDocument();
  });

  it('handles backup creation with tags', async () => {
    render(<BackupDashboard {...mockProps} />);

    // Open backup dialog
    const createButton = screen.getByText('Create Backup');
    fireEvent.click(createButton);

    // Add tags
    const tagInput = screen.getByPlaceholderText('Add tag');
    fireEvent.change(tagInput, { target: { value: 'new-tag' } });
    fireEvent.click(screen.getByText('Add'));

    // Create backup
    fireEvent.click(screen.getByText('Create'));

    await waitFor(() => {
      expect(mockProps.onBackup).toHaveBeenCalledWith('container', ['new-tag']);
    });
  });

  it('opens restore dialog when restore button is clicked', () => {
    render(<BackupDashboard {...mockProps} />);

    const restoreButtons = screen.getAllByRole('button', { name: /restore/i });
    fireEvent.click(restoreButtons[0]);

    expect(screen.getByText('Restore Backup')).toBeInTheDocument();
    expect(screen.getByText('Are you sure you want to restore this backup?')).toBeInTheDocument();
  });

  it('handles backup restoration', async () => {
    render(<BackupDashboard {...mockProps} />);

    // Open restore dialog
    const restoreButtons = screen.getAllByRole('button', { name: /restore/i });
    fireEvent.click(restoreButtons[0]);

    // Confirm restore
    fireEvent.click(screen.getByText('Restore'));

    await waitFor(() => {
      expect(mockProps.onRestore).toHaveBeenCalledWith('backup-1');
    });
  });

  it('opens delete dialog when delete button is clicked', () => {
    render(<BackupDashboard {...mockProps} />);

    const deleteButtons = screen.getAllByRole('button', { name: /delete/i });
    fireEvent.click(deleteButtons[0]);

    expect(screen.getByText('Delete Backup')).toBeInTheDocument();
    expect(screen.getByText('Are you sure you want to delete this backup?')).toBeInTheDocument();
  });

  it('handles backup deletion', async () => {
    render(<BackupDashboard {...mockProps} />);

    // Open delete dialog
    const deleteButtons = screen.getAllByRole('button', { name: /delete/i });
    fireEvent.click(deleteButtons[0]);

    // Confirm deletion
    fireEvent.click(screen.getByText('Delete'));

    await waitFor(() => {
      expect(mockProps.onDelete).toHaveBeenCalledWith('backup-1');
    });
  });

  it('displays error message when error prop is provided', () => {
    const errorMessage = 'Test error message';
    render(<BackupDashboard {...mockProps} error={errorMessage} />);

    expect(screen.getByText(errorMessage)).toBeInTheDocument();
  });

  it('disables restore button for in-progress backups', () => {
    render(<BackupDashboard {...mockProps} />);

    const restoreButtons = screen.getAllByRole('button', { name: /restore/i });
    expect(restoreButtons[1]).toBeDisabled(); // Second backup is in_progress
  });

  it('formats backup size correctly', () => {
    render(<BackupDashboard {...mockProps} />);

    expect(screen.getByText('1.00 MB')).toBeInTheDocument();
    expect(screen.getByText('2.00 MB')).toBeInTheDocument();
  });
}); 