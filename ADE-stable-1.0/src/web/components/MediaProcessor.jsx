import React, { useState, useEffect } from 'react';
import useVoiceInputStore from '../utils/voice-input';
import useImageUploadStore from '../utils/image-upload';
import axios from 'axios';

const MediaProcessor = () => {
  const [isProcessing, setIsProcessing] = useState(false);
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);

  // Voice processing state
  const {
    settings: voiceSettings,
    updateSettings: updateVoiceSettings,
    processVoiceInput,
    processingHistory: voiceHistory
  } = useVoiceInputStore();

  // Image processing state
  const {
    settings: imageSettings,
    updateSettings: updateImageSettings,
    processImageUpload,
    processingHistory: imageHistory
  } = useImageUploadStore();

  // Initialize services
  useEffect(() => {
    const initServices = async () => {
      try {
        await useVoiceInputStore.getState().initialize();
        await useImageUploadStore.getState().initialize();
      } catch (error) {
        setError('Failed to initialize services');
        console.error('Initialization error:', error);
      }
    };

    initServices();
  }, []);

  // Handle voice recording
  const handleVoiceRecording = async () => {
    try {
      setIsProcessing(true);
      setError(null);

      // Start voice recording
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream);
      const audioChunks = [];

      mediaRecorder.ondataavailable = (event) => {
        audioChunks.push(event.data);
      };

      mediaRecorder.onstop = async () => {
        const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
        await processVoiceInput(audioBlob);
        setIsProcessing(false);
      };

      mediaRecorder.start();
      setTimeout(() => mediaRecorder.stop(), 5000); // Record for 5 seconds
    } catch (error) {
      setError('Failed to record voice');
      setIsProcessing(false);
      console.error('Voice recording error:', error);
    }
  };

  // Handle image upload
  const handleImageUpload = async (event) => {
    try {
      setIsProcessing(true);
      setError(null);

      const file = event.target.files[0];
      if (!file) return;

      // Process image locally
      await processImageUpload(file);

      // Upload to server for additional processing
      const formData = new FormData();
      formData.append('file', file);
      formData.append('process_ocr', 'true');
      formData.append('analyze_image', 'true');

      const response = await axios.post('/api/media/upload/image', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });

      // Poll for results
      const mediaId = response.data.media_id;
      await pollForResults(mediaId);

      setIsProcessing(false);
    } catch (error) {
      setError('Failed to process image');
      setIsProcessing(false);
      console.error('Image processing error:', error);
    }
  };

  // Poll for processing results
  const pollForResults = async (mediaId) => {
    const maxAttempts = 10;
    let attempts = 0;

    while (attempts < maxAttempts) {
      try {
        const statusResponse = await axios.get(`/api/media/status/${mediaId}`);
        const status = statusResponse.data.status;

        if (status === 'completed') {
          const resultResponse = await axios.get(`/api/media/result/${mediaId}`);
          setResult(resultResponse.data);
          return;
        } else if (status === 'failed') {
          throw new Error('Processing failed');
        }

        await new Promise(resolve => setTimeout(resolve, 1000));
        attempts++;
      } catch (error) {
        console.error('Polling error:', error);
        throw error;
      }
    }

    throw new Error('Processing timeout');
  };

  return (
    <div className="p-4">
      <h2 className="text-2xl font-bold mb-4">Media Processor</h2>

      {/* Voice Processing Section */}
      <div className="mb-8">
        <h3 className="text-xl font-semibold mb-2">Voice Processing</h3>
        <div className="space-y-4">
          <button
            onClick={handleVoiceRecording}
            disabled={isProcessing}
            className="bg-blue-500 text-white px-4 py-2 rounded disabled:opacity-50"
          >
            {isProcessing ? 'Processing...' : 'Record Voice'}
          </button>

          {/* Voice Settings */}
          <div className="space-y-2">
            <label className="block">
              Recognition Sensitivity:
              <input
                type="range"
                min="0"
                max="1"
                step="0.1"
                value={voiceSettings.recognitionSensitivity}
                onChange={(e) => updateVoiceSettings({ recognitionSensitivity: parseFloat(e.target.value) })}
                className="ml-2"
              />
              {voiceSettings.recognitionSensitivity}
            </label>
          </div>

          {/* Voice History */}
          {voiceHistory.length > 0 && (
            <div className="mt-4">
              <h4 className="font-semibold">Recent Voice Processing</h4>
              <ul className="list-disc pl-5">
                {voiceHistory.slice(-3).map((item, index) => (
                  <li key={index}>
                    {item.text} (Confidence: {Math.round(item.confidence * 100)}%)
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      </div>

      {/* Image Processing Section */}
      <div>
        <h3 className="text-xl font-semibold mb-2">Image Processing</h3>
        <div className="space-y-4">
          <input
            type="file"
            accept="image/*"
            onChange={handleImageUpload}
            disabled={isProcessing}
            className="block w-full text-sm text-gray-500
              file:mr-4 file:py-2 file:px-4
              file:rounded-full file:border-0
              file:text-sm file:font-semibold
              file:bg-blue-50 file:text-blue-700
              hover:file:bg-blue-100"
          />

          {/* Image Settings */}
          <div className="space-y-2">
            <label className="block">
              Compression Quality:
              <input
                type="range"
                min="0"
                max="1"
                step="0.1"
                value={imageSettings.compressionQuality}
                onChange={(e) => updateImageSettings({ compressionQuality: parseFloat(e.target.value) })}
                className="ml-2"
              />
              {imageSettings.compressionQuality}
            </label>
          </div>

          {/* Image History */}
          {imageHistory.length > 0 && (
            <div className="mt-4">
              <h4 className="font-semibold">Recent Image Processing</h4>
              <ul className="list-disc pl-5">
                {imageHistory.slice(-3).map((item) => (
                  <li key={item.id}>
                    Size: {Math.round(item.size / 1024)}KB, 
                    Dimensions: {item.dimensions.width}x{item.dimensions.height}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      </div>

      {/* Results Display */}
      {result && (
        <div className="mt-8">
          <h3 className="text-xl font-semibold mb-2">Processing Results</h3>
          <pre className="bg-gray-100 p-4 rounded overflow-auto">
            {JSON.stringify(result, null, 2)}
          </pre>
        </div>
      )}

      {/* Error Display */}
      {error && (
        <div className="mt-4 p-4 bg-red-100 text-red-700 rounded">
          {error}
        </div>
      )}
    </div>
  );
};

export default MediaProcessor; 