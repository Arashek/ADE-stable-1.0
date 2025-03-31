import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import SpeechToTextInput from '../SpeechToTextInput';
import useSpeechToText from '../../hooks/useSpeechToText';

// Mock the speech-to-text hook
jest.mock('../../hooks/useSpeechToText');

describe('SpeechToTextInput', () => {
  const mockOnChange = jest.fn();
  const mockOnBlur = jest.fn();
  const mockOnFocus = jest.fn();

  const defaultProps = {
    label: 'Test Input',
    onChange: mockOnChange,
    onBlur: mockOnBlur,
    onFocus: mockOnFocus
  };

  beforeEach(() => {
    // Reset all mocks before each test
    jest.clearAllMocks();

    // Default mock implementation for useSpeechToText
    useSpeechToText.mockReturnValue({
      isListening: false,
      transcript: '',
      interimTranscript: '',
      error: null,
      startListening: jest.fn(),
      stopListening: jest.fn(),
      resetTranscript: jest.fn()
    });
  });

  it('renders correctly with default props', () => {
    render(<SpeechToTextInput {...defaultProps} />);
    
    expect(screen.getByLabelText('Test Input')).toBeInTheDocument();
    expect(screen.getByLabelText('Start recording')).toBeInTheDocument();
  });

  it('handles text input changes', async () => {
    render(<SpeechToTextInput {...defaultProps} />);
    
    const input = screen.getByLabelText('Test Input');
    await userEvent.type(input, 'test text');
    
    expect(mockOnChange).toHaveBeenCalledWith('test text');
  });

  it('handles focus and blur events', () => {
    render(<SpeechToTextInput {...defaultProps} />);
    
    const input = screen.getByLabelText('Test Input');
    
    fireEvent.focus(input);
    expect(mockOnFocus).toHaveBeenCalled();
    
    fireEvent.blur(input);
    expect(mockOnBlur).toHaveBeenCalled();
  });

  it('toggles speech recognition when mic button is clicked', () => {
    const mockStartListening = jest.fn();
    const mockStopListening = jest.fn();
    useSpeechToText.mockReturnValue({
      isListening: false,
      transcript: '',
      interimTranscript: '',
      error: null,
      startListening: mockStartListening,
      stopListening: mockStopListening,
      resetTranscript: jest.fn()
    });

    render(<SpeechToTextInput {...defaultProps} />);
    
    const micButton = screen.getByLabelText('Start recording');
    fireEvent.click(micButton);
    expect(mockStartListening).toHaveBeenCalled();
    
    // Update mock to simulate listening state
    useSpeechToText.mockReturnValue({
      isListening: true,
      transcript: '',
      interimTranscript: '',
      error: null,
      startListening: mockStartListening,
      stopListening: mockStopListening,
      resetTranscript: jest.fn()
    });
    
    fireEvent.click(micButton);
    expect(mockStopListening).toHaveBeenCalled();
  });

  it('displays interim transcript when available', () => {
    useSpeechToText.mockReturnValue({
      isListening: false,
      transcript: '',
      interimTranscript: 'interim text',
      error: null,
      startListening: jest.fn(),
      stopListening: jest.fn(),
      resetTranscript: jest.fn()
    });

    render(<SpeechToTextInput {...defaultProps} />);
    
    expect(screen.getByText('Interim: interim text')).toBeInTheDocument();
  });

  it('displays error message when speech recognition fails', () => {
    useSpeechToText.mockReturnValue({
      isListening: false,
      transcript: '',
      interimTranscript: '',
      error: 'Speech recognition error',
      startListening: jest.fn(),
      stopListening: jest.fn(),
      resetTranscript: jest.fn()
    });

    render(<SpeechToTextInput {...defaultProps} />);
    
    expect(screen.getByText('Speech recognition error')).toBeInTheDocument();
  });

  it('clears input when clear button is clicked', async () => {
    const mockResetTranscript = jest.fn();
    useSpeechToText.mockReturnValue({
      isListening: false,
      transcript: 'test text',
      interimTranscript: '',
      error: null,
      startListening: jest.fn(),
      stopListening: jest.fn(),
      resetTranscript: mockResetTranscript
    });

    render(<SpeechToTextInput {...defaultProps} value="test text" />);
    
    const clearButton = screen.getByLabelText('Clear input');
    fireEvent.click(clearButton);
    
    expect(mockOnChange).toHaveBeenCalledWith('');
    expect(mockResetTranscript).toHaveBeenCalled();
  });

  it('shows loading indicator when listening', () => {
    useSpeechToText.mockReturnValue({
      isListening: true,
      transcript: '',
      interimTranscript: '',
      error: null,
      startListening: jest.fn(),
      stopListening: jest.fn(),
      resetTranscript: jest.fn()
    });

    render(<SpeechToTextInput {...defaultProps} />);
    
    expect(screen.getByText('Listening...')).toBeInTheDocument();
  });

  it('handles disabled state correctly', () => {
    render(<SpeechToTextInput {...defaultProps} disabled />);
    
    const input = screen.getByLabelText('Test Input');
    const micButton = screen.getByLabelText('Start recording');
    
    expect(input).toBeDisabled();
    expect(micButton).toBeDisabled();
  });

  it('updates value when controlled', async () => {
    const { rerender } = render(<SpeechToTextInput {...defaultProps} value="initial" />);
    
    expect(screen.getByLabelText('Test Input')).toHaveValue('initial');
    
    rerender(<SpeechToTextInput {...defaultProps} value="updated" />);
    
    expect(screen.getByLabelText('Test Input')).toHaveValue('updated');
  });
}); 