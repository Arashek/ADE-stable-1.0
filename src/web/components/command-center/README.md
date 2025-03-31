# Command Center Multi-Modal Input System

The Command Center's multi-modal input system provides a comprehensive interface for interacting with AI agents through various input methods, including voice, text, and media inputs.

## Features

### Input Controls
- Unified input area with modality toggles
- Voice input recording and transcription
- Image attachment and preview
- Clipboard history access
- Context reference integration

### Voice Input System
- WebSpeech API integration
- Real-time transcription
- Command detection
- Multilingual support
- Voice activation controls

### Image Handling
- Drag-and-drop image attachment
- Built-in screenshot capture
- Image annotation tools
- OCR text extraction
- Image preview and editing

### Clipboard and Context
- Clipboard history management
- Content type detection
- Context reference creation
- Visual context indicators
- Context priority management

## Components

### InputControls
The main component for handling all input modalities.

```jsx
import InputControls from './InputControls';

function CommandCenter() {
  return (
    <div>
      <InputControls
        onVoiceInput={handleVoiceInput}
        onImageUpload={handleImageUpload}
        onTextInput={handleTextInput}
        onContextSelect={handleContextSelect}
      />
    </div>
  );
}
```

### Voice Recognition
Handles voice input processing and transcription.

```javascript
import { startVoiceRecognition, stopVoiceRecognition } from '../utils/voice-recognition';

// Start voice recognition
startVoiceRecognition({
  language: 'en-US',
  continuous: true,
  interimResults: true,
  onResult: (result) => {
    console.log('Transcription:', result);
  }
});

// Stop voice recognition
stopVoiceRecognition();
```

### Image Handler
Manages image processing and manipulation.

```javascript
import { processImage, captureScreenshot } from '../utils/image-handler';

// Process uploaded image
processImage(file, {
  maxSize: 1024 * 1024,
  allowedTypes: ['image/jpeg', 'image/png'],
  onProcess: (processedImage) => {
    console.log('Processed image:', processedImage);
  }
});

// Capture screenshot
captureScreenshot({
  area: 'viewport',
  format: 'png',
  onCapture: (screenshot) => {
    console.log('Screenshot captured:', screenshot);
  }
});
```

### Clipboard Manager
Handles clipboard operations and history.

```javascript
import { getClipboardHistory, addToHistory } from '../utils/clipboard-manager';

// Get clipboard history
const history = getClipboardHistory({
  maxItems: 10,
  types: ['text', 'image']
});

// Add item to history
addToHistory({
  content: 'Copied text',
  type: 'text',
  timestamp: Date.now()
});
```

## Backend Integration

### Command Center API
```python
from core.api.command_center import CommandCenterAPI

api = CommandCenterAPI()

# Process multimodal input
@api.route('/process-input')
async def process_input(input_data):
    return await api.process_multimodal_input(input_data)
```

### Voice Processing
```python
from core.api.voice_processing import VoiceProcessor

processor = VoiceProcessor()

# Process voice input
async def process_voice(audio_data):
    return await processor.transcribe(audio_data)
```

### OCR Service
```python
from core.api.ocr_service import OCRService

ocr = OCRService()

# Extract text from image
async def extract_text(image_data):
    return await ocr.extract_text(image_data)
```

### Context Management
```python
from core.api.context_management import ContextManager

manager = ContextManager()

# Create context reference
async def create_context(content):
    return await manager.create_reference(content)
```

## State Management

The input system uses Redux for state management:

```javascript
// Input state slice
const inputSlice = createSlice({
  name: 'input',
  initialState: {
    activeModality: 'text',
    voiceRecording: false,
    imagePreview: null,
    clipboardHistory: [],
    activeContexts: []
  },
  reducers: {
    setActiveModality: (state, action) => {
      state.activeModality = action.payload;
    },
    // ... other reducers
  }
});
```

## Testing

Run the test suite:
```bash
npm test src/web/components/command-center/__tests__/
```

## Accessibility

The input system follows WCAG guidelines:
- Keyboard navigation
- Screen reader support
- High contrast mode
- Focus management
- ARIA labels

## Contributing

1. Fork the repository
2. Create a feature branch
3. Implement your feature
4. Add tests
5. Create a Pull Request

## License

MIT License - see LICENSE file for details 