import { create } from 'zustand';
import useVoiceRecognitionStore from './voice-recognition';

const useVoiceInputStore = create((set, get) => ({
  // Voice processing settings
  settings: {
    speed: 1.0,
    recognitionSensitivity: 0.8,
    noiseReduction: true,
    autoPunctuation: true,
    profanityFilter: true,
    customVocabulary: [],
    accent: 'standard',
    voiceActivityDetection: true
  },

  // Processing state
  isProcessing: false,
  processingQueue: [],
  currentProcessing: null,
  processingHistory: [],
  error: null,

  // Initialize voice processing
  initialize: async () => {
    const voiceRecognition = useVoiceRecognitionStore.getState();
    if (!voiceRecognition.initialize()) {
      set({ error: 'Failed to initialize voice recognition' });
      return false;
    }

    // Initialize Web Speech API
    if ('webkitSpeechGrammarList' in window) {
      const grammarList = new window.webkitSpeechGrammarList();
      const grammar = '#JSGF V1.0; grammar commands; public <command> = ' +
        get().settings.customVocabulary.join(' | ') + ' ;';
      grammarList.addFromString(grammar, 1);
      voiceRecognition.recognition.grammars = grammarList;
    }

    return true;
  },

  // Update voice processing settings
  updateSettings: (newSettings) => {
    set(state => ({
      settings: { ...state.settings, ...newSettings }
    }));
  },

  // Process voice input with enhanced features
  processVoiceInput: async (audioData) => {
    const { settings, processingQueue } = get();
    if (get().isProcessing) {
      set({ processingQueue: [...processingQueue, audioData] });
      return;
    }

    set({ isProcessing: true, currentProcessing: audioData });

    try {
      // Apply noise reduction if enabled
      let processedAudio = settings.noiseReduction ? 
        await get().applyNoiseReduction(audioData) : audioData;

      // Process with WebSpeech API
      const recognition = useVoiceRecognitionStore.getState().recognition;
      recognition.lang = settings.accent;
      recognition.maxAlternatives = 3;

      // Start recognition
      recognition.start();
      
      // Handle results
      recognition.onresult = (event) => {
        const results = Array.from(event.results).map(result => ({
          transcript: result[0].transcript,
          confidence: result[0].confidence,
          isFinal: result.isFinal
        }));

        // Filter based on sensitivity
        const filteredResults = results.filter(
          result => result.confidence >= settings.recognitionSensitivity
        );

        if (filteredResults.length > 0) {
          const bestResult = filteredResults[0];
          
          // Apply auto-punctuation if enabled
          const processedText = settings.autoPunctuation ?
            get().applyAutoPunctuation(bestResult.transcript) :
            bestResult.transcript;

          // Apply profanity filter if enabled
          const finalText = settings.profanityFilter ?
            get().applyProfanityFilter(processedText) :
            processedText;

          // Add to processing history
          set(state => ({
            processingHistory: [...state.processingHistory, {
              text: finalText,
              confidence: bestResult.confidence,
              timestamp: Date.now()
            }]
          }));

          // Process next in queue if any
          if (processingQueue.length > 0) {
            const nextAudio = processingQueue[0];
            set({ processingQueue: processingQueue.slice(1) });
            get().processVoiceInput(nextAudio);
          } else {
            set({ isProcessing: false, currentProcessing: null });
          }
        }
      };

      recognition.onerror = (event) => {
        set({ error: event.error, isProcessing: false });
      };

    } catch (error) {
      set({ error: 'Voice processing failed', isProcessing: false });
    }
  },

  // Apply noise reduction to audio
  applyNoiseReduction: async (audioData) => {
    // Implementation using Web Audio API for noise reduction
    const audioContext = new (window.AudioContext || window.webkitAudioContext)();
    const audioBuffer = await audioContext.decodeAudioData(audioData);
    
    // Apply noise reduction processing
    const source = audioContext.createBufferSource();
    source.buffer = audioBuffer;
    
    const filter = audioContext.createBiquadFilter();
    filter.type = 'lowpass';
    filter.frequency.value = 2000;
    filter.Q.value = 1;
    
    source.connect(filter);
    filter.connect(audioContext.destination);
    
    return audioBuffer;
  },

  // Apply automatic punctuation to text
  applyAutoPunctuation: (text) => {
    // Basic punctuation rules
    const sentences = text.split(/(?<=[.!?])\s+/);
    return sentences.map(sentence => {
      if (!/[.!?]$/.test(sentence)) {
        return sentence + '.';
      }
      return sentence;
    }).join(' ');
  },

  // Apply profanity filter
  applyProfanityFilter: (text) => {
    // Implement profanity filtering logic
    const profanityList = ['bad', 'word', 'list']; // Replace with actual profanity list
    return text.replace(new RegExp(profanityList.join('|'), 'gi'), '***');
  },

  // Clear processing history
  clearHistory: () => {
    set({ processingHistory: [] });
  },

  // Get processing statistics
  getStatistics: () => {
    const { processingHistory } = get();
    return {
      totalProcessed: processingHistory.length,
      averageConfidence: processingHistory.reduce((acc, curr) => acc + curr.confidence, 0) / processingHistory.length,
      lastProcessed: processingHistory[processingHistory.length - 1]?.timestamp
    };
  }
}));

export default useVoiceInputStore; 