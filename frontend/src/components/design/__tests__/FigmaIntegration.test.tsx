import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { FigmaIntegration } from '../FigmaIntegration';
import { FigmaService } from '../../../../backend/src/services/design/FigmaService';

// Mock the FigmaService
jest.mock('../../../../backend/src/services/design/FigmaService');

describe('FigmaIntegration', () => {
  const mockOnFileSelect = jest.fn();
  const mockOnComponentSelect = jest.fn();
  const mockOnStyleSelect = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders the authentication form', () => {
    render(
      <FigmaIntegration
        onFileSelect={mockOnFileSelect}
        onComponentSelect={mockOnComponentSelect}
        onStyleSelect={mockOnStyleSelect}
      />
    );

    expect(screen.getByPlaceholderText('Figma Access Token')).toBeInTheDocument();
    expect(screen.getByPlaceholderText('Team ID')).toBeInTheDocument();
    expect(screen.getByText('Authenticate')).toBeInTheDocument();
  });

  it('handles successful authentication', async () => {
    const mockValidateAccessToken = jest.fn().mockResolvedValue(true);
    (FigmaService as jest.Mock).mockImplementation(() => ({
      validateAccessToken: mockValidateAccessToken,
      getTeamComponents: jest.fn().mockResolvedValue([]),
      getTeamStyles: jest.fn().mockResolvedValue([]),
    }));

    render(
      <FigmaIntegration
        onFileSelect={mockOnFileSelect}
        onComponentSelect={mockOnComponentSelect}
        onStyleSelect={mockOnStyleSelect}
      />
    );

    const tokenInput = screen.getByPlaceholderText('Figma Access Token');
    const teamInput = screen.getByPlaceholderText('Team ID');
    const authenticateButton = screen.getByText('Authenticate');

    fireEvent.change(tokenInput, { target: { value: 'test-token' } });
    fireEvent.change(teamInput, { target: { value: 'test-team' } });
    fireEvent.click(authenticateButton);

    await waitFor(() => {
      expect(screen.getByText('Files')).toBeInTheDocument();
    });
    expect(screen.getByText('Components')).toBeInTheDocument();
    expect(screen.getByText('Styles')).toBeInTheDocument();
  });

  it('handles failed authentication', async () => {
    const mockValidateAccessToken = jest.fn().mockResolvedValue(false);
    (FigmaService as jest.Mock).mockImplementation(() => ({
      validateAccessToken: mockValidateAccessToken,
    }));

    render(
      <FigmaIntegration
        onFileSelect={mockOnFileSelect}
        onComponentSelect={mockOnComponentSelect}
        onStyleSelect={mockOnStyleSelect}
      />
    );

    const tokenInput = screen.getByPlaceholderText('Figma Access Token');
    const teamInput = screen.getByPlaceholderText('Team ID');
    const authenticateButton = screen.getByText('Authenticate');

    fireEvent.change(tokenInput, { target: { value: 'invalid-token' } });
    fireEvent.change(teamInput, { target: { value: 'test-team' } });
    fireEvent.click(authenticateButton);

    await waitFor(() => {
      expect(screen.getByText('Invalid access token')).toBeInTheDocument();
    });
  });

  it('handles file selection', async () => {
    const mockValidateAccessToken = jest.fn().mockResolvedValue(true);
    (FigmaService as jest.Mock).mockImplementation(() => ({
      validateAccessToken: mockValidateAccessToken,
      getTeamComponents: jest.fn().mockResolvedValue([]),
      getTeamStyles: jest.fn().mockResolvedValue([]),
    }));

    render(
      <FigmaIntegration
        onFileSelect={mockOnFileSelect}
        onComponentSelect={mockOnComponentSelect}
        onStyleSelect={mockOnStyleSelect}
      />
    );

    // Authenticate first
    const tokenInput = screen.getByPlaceholderText('Figma Access Token');
    const teamInput = screen.getByPlaceholderText('Team ID');
    const authenticateButton = screen.getByText('Authenticate');

    fireEvent.change(tokenInput, { target: { value: 'test-token' } });
    fireEvent.change(teamInput, { target: { value: 'test-team' } });
    fireEvent.click(authenticateButton);

    await waitFor(() => {
      expect(screen.getByText('Design System')).toBeInTheDocument();
    });

    const fileButton = screen.getByText('Design System');
    fireEvent.click(fileButton);
    expect(mockOnFileSelect).toHaveBeenCalledWith('file1');
  });

  it('handles component selection', async () => {
    const mockComponents = [
      { key: 'comp1', name: 'Button' },
      { key: 'comp2', name: 'Input' },
    ];

    const mockValidateAccessToken = jest.fn().mockResolvedValue(true);
    (FigmaService as jest.Mock).mockImplementation(() => ({
      validateAccessToken: mockValidateAccessToken,
      getTeamComponents: jest.fn().mockResolvedValue(mockComponents),
      getTeamStyles: jest.fn().mockResolvedValue([]),
    }));

    render(
      <FigmaIntegration
        onFileSelect={mockOnFileSelect}
        onComponentSelect={mockOnComponentSelect}
        onStyleSelect={mockOnStyleSelect}
      />
    );

    // Authenticate first
    const tokenInput = screen.getByPlaceholderText('Figma Access Token');
    const teamInput = screen.getByPlaceholderText('Team ID');
    const authenticateButton = screen.getByText('Authenticate');

    fireEvent.change(tokenInput, { target: { value: 'test-token' } });
    fireEvent.change(teamInput, { target: { value: 'test-team' } });
    fireEvent.click(authenticateButton);

    await waitFor(() => {
      expect(screen.getByText('Button')).toBeInTheDocument();
    });

    const componentButton = screen.getByText('Button');
    fireEvent.click(componentButton);
    expect(mockOnComponentSelect).toHaveBeenCalledWith('comp1');
  });

  it('handles style selection', async () => {
    const mockStyles = [
      { key: 'style1', name: 'Primary Color' },
      { key: 'style2', name: 'Secondary Color' },
    ];

    const mockValidateAccessToken = jest.fn().mockResolvedValue(true);
    (FigmaService as jest.Mock).mockImplementation(() => ({
      validateAccessToken: mockValidateAccessToken,
      getTeamComponents: jest.fn().mockResolvedValue([]),
      getTeamStyles: jest.fn().mockResolvedValue(mockStyles),
    }));

    render(
      <FigmaIntegration
        onFileSelect={mockOnFileSelect}
        onComponentSelect={mockOnComponentSelect}
        onStyleSelect={mockOnStyleSelect}
      />
    );

    // Authenticate first
    const tokenInput = screen.getByPlaceholderText('Figma Access Token');
    const teamInput = screen.getByPlaceholderText('Team ID');
    const authenticateButton = screen.getByText('Authenticate');

    fireEvent.change(tokenInput, { target: { value: 'test-token' } });
    fireEvent.change(teamInput, { target: { value: 'test-team' } });
    fireEvent.click(authenticateButton);

    await waitFor(() => {
      expect(screen.getByText('Primary Color')).toBeInTheDocument();
    });

    const styleButton = screen.getByText('Primary Color');
    fireEvent.click(styleButton);
    expect(mockOnStyleSelect).toHaveBeenCalledWith('style1');
  });

  it('handles loading state', async () => {
    const mockValidateAccessToken = jest.fn().mockImplementation(() => new Promise(resolve => setTimeout(resolve, 100)));
    (FigmaService as jest.Mock).mockImplementation(() => ({
      validateAccessToken: mockValidateAccessToken,
    }));

    render(
      <FigmaIntegration
        onFileSelect={mockOnFileSelect}
        onComponentSelect={mockOnComponentSelect}
        onStyleSelect={mockOnStyleSelect}
      />
    );

    const tokenInput = screen.getByPlaceholderText('Figma Access Token');
    const teamInput = screen.getByPlaceholderText('Team ID');
    const authenticateButton = screen.getByText('Authenticate');

    fireEvent.change(tokenInput, { target: { value: 'test-token' } });
    fireEvent.change(teamInput, { target: { value: 'test-team' } });
    fireEvent.click(authenticateButton);

    expect(screen.getByText('Authenticating...')).toBeInTheDocument();
  });
}); 