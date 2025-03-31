import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import { GitIntegration } from '../GitIntegration';
import { GitService } from '../../../services/git/GitService';

// Mock the GitService
jest.mock('../../../services/git/GitService');

const mockGitStatus = {
  branch: 'main',
  modified: ['src/App.tsx', 'src/components/FileExplorer/GitIntegration.tsx'],
  staged: ['package.json'],
  untracked: ['temp.txt'],
  ahead: 2,
  behind: 1,
};

const theme = createTheme();

describe('GitIntegration', () => {
  let mockConnect: jest.Mock;
  let mockPush: jest.Mock;
  let mockPull: jest.Mock;
  let mockGetStatus: jest.Mock;
  let mockStage: jest.Mock;
  let mockUnstage: jest.Mock;
  let mockCommit: jest.Mock;

  beforeEach(() => {
    mockConnect = jest.fn().mockResolvedValue(true);
    mockPush = jest.fn().mockResolvedValue(true);
    mockPull = jest.fn().mockResolvedValue(true);
    mockGetStatus = jest.fn().mockResolvedValue(mockGitStatus);
    mockStage = jest.fn().mockResolvedValue(true);
    mockUnstage = jest.fn().mockResolvedValue(true);
    mockCommit = jest.fn().mockResolvedValue(true);

    (GitService.getInstance as jest.Mock).mockReturnValue({
      connect: mockConnect,
      push: mockPush,
      pull: mockPull,
      getStatus: mockGetStatus,
      stage: mockStage,
      unstage: mockUnstage,
      commit: mockCommit,
    });
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  it('renders the Git integration menu button', () => {
    render(
      <ThemeProvider theme={theme}>
        <GitIntegration />
      </ThemeProvider>
    );

    expect(screen.getByTitle('Git Menu')).toBeInTheDocument();
  });

  it('opens the connect dialog when clicking connect button', () => {
    render(
      <ThemeProvider theme={theme}>
        <GitIntegration />
      </ThemeProvider>
    );

    fireEvent.click(screen.getByTitle('Git Menu'));
    fireEvent.click(screen.getByText('Connect to Repository'));

    expect(screen.getByText('Connect to Git Repository')).toBeInTheDocument();
  });

  it('handles repository connection', async () => {
    render(
      <ThemeProvider theme={theme}>
        <GitIntegration />
      </ThemeProvider>
    );

    fireEvent.click(screen.getByTitle('Git Menu'));
    fireEvent.click(screen.getByText('Connect to Repository'));

    const urlInput = screen.getByLabelText('Repository URL');
    const usernameInput = screen.getByLabelText('Username');
    const passwordInput = screen.getByLabelText('Password');

    fireEvent.change(urlInput, { target: { value: 'https://github.com/user/repo.git' } });
    fireEvent.change(usernameInput, { target: { value: 'testuser' } });
    fireEvent.change(passwordInput, { target: { value: 'testpass' } });

    fireEvent.click(screen.getByText('Connect'));

    await waitFor(() => {
      expect(mockConnect).toHaveBeenCalledWith({
        url: 'https://github.com/user/repo.git',
        username: 'testuser',
        password: 'testpass',
      });
    });
  });

  it('displays Git status after connecting', async () => {
    render(
      <ThemeProvider theme={theme}>
        <GitIntegration />
      </ThemeProvider>
    );

    // Simulate successful connection
    mockConnect.mockResolvedValueOnce(true);
    mockGetStatus.mockResolvedValueOnce(mockGitStatus);

    fireEvent.click(screen.getByTitle('Git Menu'));
    fireEvent.click(screen.getByText('Connect to Repository'));

    const urlInput = screen.getByLabelText('Repository URL');
    fireEvent.change(urlInput, { target: { value: 'https://github.com/user/repo.git' } });
    fireEvent.click(screen.getByText('Connect'));

    await waitFor(() => {
      expect(screen.getByText('main')).toBeInTheDocument();
    });

    await waitFor(() => {
      expect(screen.getByText('2 ahead, 1 behind')).toBeInTheDocument();
    });
  });

  it('handles staging files', async () => {
    render(
      <ThemeProvider theme={theme}>
        <GitIntegration />
      </ThemeProvider>
    );

    // Simulate connected state
    mockGetStatus.mockResolvedValueOnce(mockGitStatus);

    fireEvent.click(screen.getByTitle('Git Menu'));
    fireEvent.click(screen.getByText('View Changes'));

    await waitFor(() => {
      expect(screen.getByText('src/App.tsx')).toBeInTheDocument();
    });

    const stageButton = screen.getAllByTitle('Stage file')[0];
    fireEvent.click(stageButton);

    await waitFor(() => {
      expect(mockStage).toHaveBeenCalledWith('src/App.tsx');
    });
  });

  it('handles committing changes', async () => {
    render(
      <ThemeProvider theme={theme}>
        <GitIntegration />
      </ThemeProvider>
    );

    // Simulate connected state with staged changes
    mockGetStatus.mockResolvedValueOnce(mockGitStatus);

    fireEvent.click(screen.getByTitle('Git Menu'));
    fireEvent.click(screen.getByText('Commit Changes'));

    const messageInput = screen.getByLabelText('Commit Message');
    fireEvent.change(messageInput, { target: { value: 'Test commit message' } });
    fireEvent.click(screen.getByText('Commit'));

    await waitFor(() => {
      expect(mockCommit).toHaveBeenCalledWith('Test commit message');
    });
  });

  it('handles pulling changes', async () => {
    render(
      <ThemeProvider theme={theme}>
        <GitIntegration />
      </ThemeProvider>
    );

    fireEvent.click(screen.getByTitle('Git Menu'));
    fireEvent.click(screen.getByText('Pull Changes'));

    await waitFor(() => {
      expect(mockPull).toHaveBeenCalled();
    });
  });

  it('handles pushing changes', async () => {
    render(
      <ThemeProvider theme={theme}>
        <GitIntegration />
      </ThemeProvider>
    );

    fireEvent.click(screen.getByTitle('Git Menu'));
    fireEvent.click(screen.getByText('Push Changes'));

    await waitFor(() => {
      expect(mockPush).toHaveBeenCalled();
    });
  });

  it('displays error messages', async () => {
    mockConnect.mockRejectedValueOnce(new Error('Connection failed'));

    render(
      <ThemeProvider theme={theme}>
        <GitIntegration />
      </ThemeProvider>
    );

    fireEvent.click(screen.getByTitle('Git Menu'));
    fireEvent.click(screen.getByText('Connect to Repository'));

    const urlInput = screen.getByLabelText('Repository URL');
    fireEvent.change(urlInput, { target: { value: 'https://github.com/user/repo.git' } });
    fireEvent.click(screen.getByText('Connect'));

    await waitFor(() => {
      expect(screen.getByText('Connection failed')).toBeInTheDocument();
    });
  });

  it('updates status automatically after operations', async () => {
    render(
      <ThemeProvider theme={theme}>
        <GitIntegration />
      </ThemeProvider>
    );

    // Simulate successful commit
    mockCommit.mockResolvedValueOnce(true);
    const updatedStatus = { ...mockGitStatus, staged: [] };
    mockGetStatus.mockResolvedValueOnce(mockGitStatus)
                .mockResolvedValueOnce(updatedStatus);

    fireEvent.click(screen.getByTitle('Git Menu'));
    fireEvent.click(screen.getByText('Commit Changes'));

    const messageInput = screen.getByLabelText('Commit Message');
    fireEvent.change(messageInput, { target: { value: 'Test commit' } });
    fireEvent.click(screen.getByText('Commit'));

    await waitFor(() => {
      expect(mockGetStatus).toHaveBeenCalledTimes(2);
    });
  });
}); 