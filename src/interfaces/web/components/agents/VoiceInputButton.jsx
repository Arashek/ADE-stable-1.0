import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { FaMicrophone, FaMicrophoneSlash } from 'react-icons/fa';
import PropTypes from 'prop-types';

const Button = styled.button`
  background: ${props => props.isRecording ? '#ef4444' : '#3b82f6'};
  color: white;
  border: none;
  border-radius: 8px;
  padding: 8px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;

  &:hover {
    background: ${props => props.isRecording ? '#dc2626' : '#2563eb'};
  }

  &:disabled {
    background: #94a3b8;
    cursor: not-allowed;
  }
`;

const RecordingIndicator = styled.div`
  position: absolute;
  top: -8px;
  right: -8px;
  width: 12px;
  height: 12px;
  background: #ef4444;
  border-radius: 50%;
  animation: pulse 1.5s infinite;

  @keyframes pulse {
    0% {
      transform: scale(1);
      opacity: 1;
    }
    50% {
      transform: scale(1.2);
      opacity: 0.5;
    }
    100% {
      transform: scale(1);
      opacity: 1;
    }
  }
`;

const VoiceInputButton = ({ onTranscript }) => {
  const [isRecording, setIsRecording] = useState(false);
  const [recognition, setRecognition] = useState(null);

  useEffect(() => {
    if ('webkitSpeechRecognition' in window) {
      const recognition = new window.webkitSpeechRecognition();
      recognition.continuous = false;
      recognition.interimResults = false;
      recognition.lang = 'en-US';

      recognition.onstart = () => {
        setIsRecording(true);
      };

      recognition.onend = () => {
        setIsRecording(false);
      };

      recognition.onresult = (event) => {
        const transcript = event.results[0][0].transcript;
        onTranscript(transcript);
      };

      recognition.onerror = (event) => {
        console.error('Speech recognition error:', event.error);
        setIsRecording(false);
      };

      setRecognition(recognition);
    }
  }, [onTranscript]);

  const toggleRecording = () => {
    if (!recognition) {
      console.error('Speech recognition not supported');
      return;
    }

    if (isRecording) {
      recognition.stop();
    } else {
      recognition.start();
    }
  };

  return (
    <Button
      type="button"
      onClick={toggleRecording}
      isRecording={isRecording}
      disabled={!recognition}
      title={recognition ? 'Click to start/stop voice input' : 'Voice input not supported'}
    >
      {isRecording ? <FaMicrophoneSlash /> : <FaMicrophone />}
      {isRecording && <RecordingIndicator />}
    </Button>
  );
};

VoiceInputButton.propTypes = {
  onTranscript: PropTypes.func.isRequired,
};

export default VoiceInputButton; 