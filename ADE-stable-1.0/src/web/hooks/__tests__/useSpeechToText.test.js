import { renderHook, act } from '@testing-library/react';
import useSpeechToText from '../useSpeechToText';

// Mock the Web Speech API
const mockSpeechRecognition = {
  continuous: false,
  interimResults: true,
  lang: 'en-US',
  start: jest.fn(),
  stop: jest.fn(),
  onstart: null,
  onresult: null,
  onerror: null,
  onend: null
};

window.webkitSpeechRecognition = jest.fn(() => mockSpeechRecognition);

describe('useSpeechToText', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('initializes with default values', () => {
    const { result } = renderHook(() => useSpeechToText());

    expect(result.current.isListening).toBe(false);
    expect(result.current.transcript).toBe('');
    expect(result.current.interimTranscript).toBe('');
    expect(result.current.error).toBe(null);
  });

  it('handles speech recognition start', () => {
    const onStart = jest.fn();
    const { result } = renderHook(() => useSpeechToText({ onStart }));

    act(() => {
      result.current.startListening();
    });

    expect(mockSpeechRecognition.start).toHaveBeenCalled();
    expect(onStart).toHaveBeenCalled();
  });

  it('handles speech recognition stop', () => {
    const onEnd = jest.fn();
    const { result } = renderHook(() => useSpeechToText({ onEnd }));

    act(() => {
      result.current.startListening();
      result.current.stopListening();
    });

    expect(mockSpeechRecognition.stop).toHaveBeenCalled();
    expect(onEnd).toHaveBeenCalled();
  });

  it('processes speech recognition results', () => {
    const onResult = jest.fn();
    const { result } = renderHook(() => useSpeechToText({ onResult }));

    act(() => {
      result.current.startListening();
      mockSpeechRecognition.onresult({
        resultIndex: 0,
        results: [
          [{ transcript: 'final text', isFinal: true }],
          [{ transcript: 'interim text', isFinal: false }]
        ]
      });
    });

    expect(result.current.transcript).toBe('final text');
    expect(result.current.interimTranscript).toBe('interim text');
    expect(onResult).toHaveBeenCalledWith('final text', 'interim text');
  });

  it('handles speech recognition errors', () => {
    const onError = jest.fn();
    const { result } = renderHook(() => useSpeechToText({ onError }));

    act(() => {
      result.current.startListening();
      mockSpeechRecognition.onerror({ error: 'test error' });
    });

    expect(result.current.error).toBe('Speech recognition error: test error');
    expect(onError).toHaveBeenCalledWith('test error');
  });

  it('handles browser compatibility', () => {
    // Simulate browser without speech recognition
    window.webkitSpeechRecognition = undefined;

    const onError = jest.fn();
    const { result } = renderHook(() => useSpeechToText({ onError }));

    expect(result.current.error).toBe('Speech recognition is not supported in this browser');
    expect(onError).toHaveBeenCalledWith('browser_not_supported');
  });

  it('resets transcript', () => {
    const { result } = renderHook(() => useSpeechToText());

    act(() => {
      result.current.startListening();
      mockSpeechRecognition.onresult({
        resultIndex: 0,
        results: [{ transcript: 'test text', isFinal: true }]
      });
      result.current.resetTranscript();
    });

    expect(result.current.transcript).toBe('');
    expect(result.current.interimTranscript).toBe('');
    expect(result.current.error).toBe(null);
  });

  it('cleans up on unmount', () => {
    const { unmount } = renderHook(() => useSpeechToText());

    unmount();
    expect(mockSpeechRecognition.stop).toHaveBeenCalled();
  });

  it('handles continuous mode', () => {
    renderHook(() => useSpeechToText({ continuous: true }));
    expect(mockSpeechRecognition.continuous).toBe(true);
  });

  it('handles interim results', () => {
    renderHook(() => useSpeechToText({ interimResults: false }));
    expect(mockSpeechRecognition.interimResults).toBe(false);
  });

  it('handles language setting', () => {
    renderHook(() => useSpeechToText({ language: 'es-ES' }));
    expect(mockSpeechRecognition.lang).toBe('es-ES');
  });
}); 