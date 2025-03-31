import { renderHook, act } from '@testing-library/react-hooks';
import { useVoiceRecorder } from '../useVoiceRecorder';

// Mock MediaRecorder
class MockMediaRecorder {
  private stream: MediaStream;
  private dataAvailableHandler: ((event: { data: Blob }) => void) | null = null;
  private stopHandler: (() => void) | null = null;
  private isRecording = false;

  constructor(stream: MediaStream) {
    this.stream = stream;
  }

  start() {
    this.isRecording = true;
    // Simulate data chunks
    setInterval(() => {
      if (this.isRecording && this.dataAvailableHandler) {
        this.dataAvailableHandler({ data: new Blob(['test'], { type: 'audio/webm' }) });
      }
    }, 1000);
  }

  stop() {
    this.isRecording = false;
    if (this.stopHandler) {
      this.stopHandler();
    }
  }

  pause() {
    this.isRecording = false;
  }

  resume() {
    this.isRecording = true;
  }

  set ondataavailable(handler: (event: { data: Blob }) => void) {
    this.dataAvailableHandler = handler;
  }

  set onstop(handler: () => void) {
    this.stopHandler = handler;
  }
}

// Mock getUserMedia
const mockGetUserMedia = jest.fn().mockResolvedValue({
  getTracks: () => [{ stop: jest.fn() }]
});

Object.defineProperty(global.navigator.mediaDevices, 'getUserMedia', {
  value: mockGetUserMedia,
});

// Mock MediaRecorder
Object.defineProperty(window, 'MediaRecorder', {
  value: MockMediaRecorder,
});

describe('useVoiceRecorder', () => {
  beforeEach(() => {
    jest.useFakeTimers();
    jest.clearAllMocks();
  });

  afterEach(() => {
    jest.useRealTimers();
  });

  it('should initialize with default values', () => {
    const { result } = renderHook(() => useVoiceRecorder());

    expect(result.current.isRecording).toBe(false);
    expect(result.current.duration).toBe(0);
  });

  it('should start recording', async () => {
    const onRecordingComplete = jest.fn();
    const { result } = renderHook(() => useVoiceRecorder({ onRecordingComplete }));

    await act(async () => {
      await result.current.startRecording();
    });

    expect(result.current.isRecording).toBe(true);
    expect(mockGetUserMedia).toHaveBeenCalledWith({ audio: true });
  });

  it('should stop recording', async () => {
    const onRecordingComplete = jest.fn();
    const { result } = renderHook(() => useVoiceRecorder({ onRecordingComplete }));

    await act(async () => {
      await result.current.startRecording();
    });

    expect(result.current.isRecording).toBe(true);

    await act(async () => {
      result.current.stopRecording();
    });

    expect(result.current.isRecording).toBe(false);
    expect(onRecordingComplete).toHaveBeenCalled();
  });

  it('should update duration while recording', async () => {
    const { result } = renderHook(() => useVoiceRecorder());

    await act(async () => {
      await result.current.startRecording();
    });

    // Simulate time passing
    act(() => {
      jest.advanceTimersByTime(2000);
    });

    expect(result.current.duration).toBe(2);
  });

  it('should stop recording after max duration', async () => {
    const onRecordingComplete = jest.fn();
    const { result } = renderHook(() => useVoiceRecorder({
      maxDuration: 3,
      onRecordingComplete
    }));

    await act(async () => {
      await result.current.startRecording();
    });

    // Simulate time passing beyond max duration
    act(() => {
      jest.advanceTimersByTime(4000);
    });

    expect(result.current.isRecording).toBe(false);
    expect(onRecordingComplete).toHaveBeenCalled();
  });

  it('should handle pause and resume', async () => {
    const { result } = renderHook(() => useVoiceRecorder());

    await act(async () => {
      await result.current.startRecording();
    });

    expect(result.current.isRecording).toBe(true);

    await act(async () => {
      result.current.pauseRecording();
    });

    expect(result.current.isRecording).toBe(false);

    await act(async () => {
      result.current.resumeRecording();
    });

    expect(result.current.isRecording).toBe(true);
  });

  it('should handle errors when starting recording', async () => {
    mockGetUserMedia.mockRejectedValueOnce(new Error('Permission denied'));
    const { result } = renderHook(() => useVoiceRecorder());

    await act(async () => {
      await result.current.startRecording();
    });

    expect(result.current.isRecording).toBe(false);
  });
}); 