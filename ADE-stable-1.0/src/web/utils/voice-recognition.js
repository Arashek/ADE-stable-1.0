import { create } from 'zustand';

const useVoiceRecognitionStore = create((set, get) => ({
  isListening: false,
  transcript: '',
  language: 'en-US',
  commands: new Map(),
  error: null,
  recognition: null,
  interimTranscript: '',
  finalTranscript: '',
  visualFeedback: false,
  autoStop: true,
  continuous: false,
  maxAlternatives: 1,
  confidence: 0,
  lastCommand: null,
  commandHistory: [],
  supportedLanguages: [
    { code: 'en-US', name: 'English (US)' },
    { code: 'en-GB', name: 'English (UK)' },
    { code: 'es-ES', name: 'Spanish' },
    { code: 'fr-FR', name: 'French' },
    { code: 'de-DE', name: 'German' },
    { code: 'it-IT', name: 'Italian' },
    { code: 'pt-PT', name: 'Portuguese' },
    { code: 'ru-RU', name: 'Russian' },
    { code: 'ja-JP', name: 'Japanese' },
    { code: 'ko-KR', name: 'Korean' },
    { code: 'zh-CN', name: 'Chinese (Simplified)' }
  ],

  initialize: () => {
    if (!('webkitSpeechRecognition' in window)) {
      set({ error: 'Speech recognition not supported in this browser' });
      return false;
    }

    const recognition = new window.webkitSpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = true;
    recognition.maxAlternatives = 1;

    recognition.onstart = () => {
      set({ isListening: true, error: null });
    };

    recognition.onerror = (event) => {
      set({ error: event.error, isListening: false });
    };

    recognition.onend = () => {
      const { autoStop, continuous } = get();
      if (autoStop && !continuous) {
        set({ isListening: false });
      }
    };

    recognition.onresult = (event) => {
      const { interimTranscript, finalTranscript } = get();
      let newInterimTranscript = '';
      let newFinalTranscript = finalTranscript;

      for (let i = event.resultIndex; i < event.results.length; i++) {
        const transcript = event.results[i][0].transcript;
        if (event.results[i].isFinal) {
          newFinalTranscript += transcript;
        } else {
          newInterimTranscript += transcript;
        }
      }

      set({
        interimTranscript: newInterimTranscript,
        finalTranscript: newFinalTranscript,
        transcript: newFinalTranscript + newInterimTranscript
      });

      // Process commands
      const { processCommands } = get();
      processCommands(newFinalTranscript + newInterimTranscript);
    };

    set({ recognition });
    return true;
  },

  startListening: () => {
    const { recognition, language, continuous } = get();
    if (!recognition) return false;

    recognition.lang = language;
    recognition.continuous = continuous;
    recognition.start();
    return true;
  },

  stopListening: () => {
    const { recognition } = get();
    if (!recognition) return false;

    recognition.stop();
    set({ isListening: false });
    return true;
  },

  setLanguage: (langCode) => {
    set({ language: langCode });
  },

  registerCommand: (command, callback) => {
    const { commands } = get();
    commands.set(command.toLowerCase(), callback);
    set({ commands });
  },

  processCommands: (text) => {
    const { commands, commandHistory } = get();
    const lowerText = text.toLowerCase();

    for (const [command, callback] of commands) {
      if (lowerText.includes(command)) {
        const newHistory = [...commandHistory, { command, text, timestamp: Date.now() }];
        set({ commandHistory: newHistory, lastCommand: command });
        callback(text);
        break;
      }
    }
  },

  setVisualFeedback: (enabled) => {
    set({ visualFeedback: enabled });
  },

  setAutoStop: (enabled) => {
    set({ autoStop: enabled });
  },

  setContinuous: (enabled) => {
    set({ continuous: enabled });
  },

  clearTranscript: () => {
    set({
      transcript: '',
      interimTranscript: '',
      finalTranscript: '',
      lastCommand: null
    });
  },

  getCommandHistory: () => {
    return get().commandHistory;
  },

  getSupportedLanguages: () => {
    return get().supportedLanguages;
  }
}));

export default useVoiceRecognitionStore; 