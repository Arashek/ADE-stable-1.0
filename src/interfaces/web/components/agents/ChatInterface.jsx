import React, { useState, useRef, useEffect } from 'react';
import styled from 'styled-components';
import { FaPaperPlane, FaTimes } from 'react-icons/fa';
import PropTypes from 'prop-types';
import VoiceInputButton from './VoiceInputButton';

const ChatContainer = styled.div`
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  padding: 24px;
`;

const MessagesContainer = styled.div`
  flex: 1;
  overflow-y: auto;
  padding-right: 8px;
  margin-bottom: 24px;

  &::-webkit-scrollbar {
    width: 6px;
  }

  &::-webkit-scrollbar-track {
    background: #f1f5f9;
    border-radius: 3px;
  }

  &::-webkit-scrollbar-thumb {
    background: #cbd5e1;
    border-radius: 3px;

    &:hover {
      background: #94a3b8;
    }
  }
`;

const Message = styled.div`
  display: flex;
  margin-bottom: 16px;
  flex-direction: ${props => props.sender === 'user' ? 'row-reverse' : 'row'};
`;

const MessageContent = styled.div`
  max-width: 70%;
  padding: 12px 16px;
  border-radius: 12px;
  background: ${props => props.sender === 'user' ? '#3b82f6' : 'white'};
  color: ${props => props.sender === 'user' ? 'white' : '#1e293b'};
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
`;

const MessageText = styled.p`
  margin: 0;
  font-size: 14px;
  line-height: 1.5;
  white-space: pre-wrap;
`;

const MessageTime = styled.span`
  font-size: 12px;
  color: ${props => props.sender === 'user' ? 'rgba(255, 255, 255, 0.7)' : '#64748b'};
  margin-top: 4px;
  display: block;
`;

const InputContainer = styled.div`
  display: flex;
  gap: 12px;
  align-items: flex-end;
  background: white;
  padding: 16px;
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
`;

const TextArea = styled.textarea`
  flex: 1;
  min-height: 24px;
  max-height: 120px;
  padding: 8px 12px;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  resize: none;
  font-size: 14px;
  line-height: 1.5;
  color: #1e293b;
  background: #f8fafc;

  &:focus {
    outline: none;
    border-color: #3b82f6;
    box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.1);
  }
`;

const SendButton = styled.button`
  background: #3b82f6;
  color: white;
  border: none;
  border-radius: 8px;
  padding: 8px 16px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.2s;

  &:hover {
    background: #2563eb;
  }

  &:disabled {
    background: #94a3b8;
    cursor: not-allowed;
  }
`;

const AttachmentsContainer = styled.div`
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 12px;
`;

const Attachment = styled.div`
  display: flex;
  align-items: center;
  gap: 8px;
  background: #f1f5f9;
  padding: 6px 12px;
  border-radius: 6px;
  font-size: 14px;
  color: #64748b;
`;

const RemoveAttachment = styled.button`
  background: none;
  border: none;
  color: #64748b;
  cursor: pointer;
  padding: 2px;
  display: flex;
  align-items: center;
  justify-content: center;

  &:hover {
    color: #ef4444;
  }
`;

const ChatInterface = ({
  messages,
  onSendMessage,
  loading,
  attachments,
  onRemoveAttachment,
}) => {
  const [input, setInput] = useState('');
  const textareaRef = useRef(null);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (input.trim() && !loading) {
      onSendMessage(input.trim());
      setInput('');
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${textareaRef.current.scrollHeight}px`;
    }
  }, [input]);

  const formatTime = (timestamp) => {
    return new Date(timestamp).toLocaleTimeString([], {
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  return (
    <ChatContainer>
      <MessagesContainer>
        {messages.map((message) => (
          <Message key={message.id} sender={message.sender}>
            <MessageContent sender={message.sender}>
              <MessageText>{message.content}</MessageText>
              <MessageTime sender={message.sender}>
                {formatTime(message.timestamp)}
              </MessageTime>
            </MessageContent>
          </Message>
        ))}
      </MessagesContainer>

      <form onSubmit={handleSubmit}>
        <InputContainer>
          <TextArea
            ref={textareaRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Type your message..."
            rows={1}
          />
          <VoiceInputButton onTranscript={setInput} />
          <SendButton type="submit" disabled={!input.trim() || loading}>
            <FaPaperPlane />
            Send
          </SendButton>
        </InputContainer>
      </form>

      {attachments.length > 0 && (
        <AttachmentsContainer>
          {attachments.map((file, index) => (
            <Attachment key={index}>
              {file.name}
              <RemoveAttachment
                type="button"
                onClick={() => onRemoveAttachment(index)}
              >
                <FaTimes />
              </RemoveAttachment>
            </Attachment>
          ))}
        </AttachmentsContainer>
      )}
    </ChatContainer>
  );
};

ChatInterface.propTypes = {
  messages: PropTypes.arrayOf(
    PropTypes.shape({
      id: PropTypes.string.isRequired,
      content: PropTypes.string.isRequired,
      sender: PropTypes.oneOf(['user', 'agent']).isRequired,
      timestamp: PropTypes.string.isRequired,
    })
  ).isRequired,
  onSendMessage: PropTypes.func.isRequired,
  loading: PropTypes.bool.isRequired,
  attachments: PropTypes.arrayOf(PropTypes.instanceOf(File)).isRequired,
  onRemoveAttachment: PropTypes.func.isRequired,
};

export default ChatInterface; 