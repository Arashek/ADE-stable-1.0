import React, { useState, useRef } from 'react';
import { Box, IconButton, TextField, Tooltip } from '@mui/material';
import {
  Send as SendIcon,
  AttachFile as AttachFileIcon,
  Image as ImageIcon,
  Mic as MicIcon,
  Stop as StopIcon
} from '@mui/icons-material';
import { styled } from '@mui/material/styles';

const InputContainer = styled(Box)(({ theme }) => ({
  display: 'flex',
  alignItems: 'center',
  padding: theme.spacing(1),
  borderTop: `1px solid ${theme.palette.divider}`,
  backgroundColor: theme.palette.background.paper,
}));

const HiddenInput = styled('input')({
  display: 'none',
});

interface ChatInputProps {
  onSendMessage: (message: string, media?: File) => void;
  onStartRecording: () => void;
  onStopRecording: () => void;
  isRecording: boolean;
  disabled?: boolean;
}

export const ChatInput: React.FC<ChatInputProps> = ({
  onSendMessage,
  onStartRecording,
  onStopRecording,
  isRecording,
  disabled = false,
}) => {
  const [message, setMessage] = useState('');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const imageInputRef = useRef<HTMLInputElement>(null);

  const handleSend = () => {
    if (message.trim() || selectedFile) {
      onSendMessage(message, selectedFile || undefined);
      setMessage('');
      setSelectedFile(null);
    }
  };

  const handleKeyPress = (event: React.KeyboardEvent) => {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      handleSend();
    }
  };

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      setSelectedFile(file);
    }
  };

  const handleImageSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file && file.type.startsWith('image/')) {
      setSelectedFile(file);
    }
  };

  return (
    <InputContainer>
      <HiddenInput
        type="file"
        ref={fileInputRef}
        onChange={handleFileSelect}
        accept="*/*"
      />
      <HiddenInput
        type="file"
        ref={imageInputRef}
        onChange={handleImageSelect}
        accept="image/*"
      />
      
      <Tooltip title="Attach File">
        <IconButton
          onClick={() => fileInputRef.current?.click()}
          disabled={disabled || isRecording}
        >
          <AttachFileIcon />
        </IconButton>
      </Tooltip>

      <Tooltip title="Upload Image">
        <IconButton
          onClick={() => imageInputRef.current?.click()}
          disabled={disabled || isRecording}
        >
          <ImageIcon />
        </IconButton>
      </Tooltip>

      <Tooltip title={isRecording ? "Stop Recording" : "Start Recording"}>
        <IconButton
          onClick={isRecording ? onStopRecording : onStartRecording}
          disabled={disabled}
          color={isRecording ? "error" : "default"}
        >
          {isRecording ? <StopIcon /> : <MicIcon />}
        </IconButton>
      </Tooltip>

      <TextField
        fullWidth
        multiline
        maxRows={4}
        value={message}
        onChange={(e) => setMessage(e.target.value)}
        onKeyPress={handleKeyPress}
        placeholder="Type a message..."
        disabled={disabled || isRecording}
        sx={{ mx: 1 }}
      />

      <Tooltip title="Send Message">
        <IconButton
          onClick={handleSend}
          disabled={disabled || isRecording || (!message.trim() && !selectedFile)}
          color="primary"
        >
          <SendIcon />
        </IconButton>
      </Tooltip>
    </InputContainer>
  );
}; 