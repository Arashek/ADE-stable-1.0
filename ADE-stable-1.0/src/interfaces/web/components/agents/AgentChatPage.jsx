import React, { useState, useEffect, useRef } from 'react';
import styled from 'styled-components';
import { FaPaperclip, FaExclamationTriangle } from 'react-icons/fa';
import PropTypes from 'prop-types';
import ChatInterface from './ChatInterface';
import AgentOutputDisplay from './AgentOutputDisplay';
import VoiceInputButton from './VoiceInputButton';
import { agentService } from '../../services/agentService';

const ChatContainer = styled.div`
  display: flex;
  flex-direction: column;
  height: 100%;
  background: #f8fafc;
`;

const ChatHeader = styled.div`
  padding: 16px 24px;
  background: white;
  border-bottom: 1px solid #e2e8f0;
  display: flex;
  justify-content: space-between;
  align-items: center;
`;

const AgentInfo = styled.div`
  display: flex;
  align-items: center;
  gap: 12px;
`;

const AgentAvatar = styled.div`
  width: 40px;
  height: 40px;
  background: ${props => props.color};
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 20px;
`;

const AgentDetails = styled.div`
  display: flex;
  flex-direction: column;
`;

const AgentName = styled.h2`
  font-size: 18px;
  color: #1e293b;
  margin: 0;
`;

const AgentStatus = styled.span`
  font-size: 14px;
  color: #64748b;
`;

const FileUpload = styled.div`
  position: relative;
  display: flex;
  align-items: center;
  gap: 8px;
`;

const FileInput = styled.input`
  display: none;
`;

const UploadButton = styled.button`
  background: none;
  border: none;
  color: #64748b;
  cursor: pointer;
  padding: 8px;
  border-radius: 4px;
  display: flex;
  align-items: center;
  gap: 4px;
  transition: all 0.2s;

  &:hover {
    background: #f1f5f9;
    color: #1e293b;
  }
`;

const ErrorMessage = styled.div`
  display: flex;
  align-items: center;
  gap: 8px;
  background: #fee2e2;
  color: #991b1b;
  padding: 12px 16px;
  margin: 16px 24px;
  border-radius: 6px;
`;

const AgentChatPage = ({ agent }) => {
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [attachments, setAttachments] = useState([]);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = async (message, type = 'text') => {
    try {
      setLoading(true);
      setError(null);

      // Add user message to chat
      const userMessage = {
        id: Date.now().toString(),
        type,
        content: message,
        sender: 'user',
        timestamp: new Date().toISOString(),
      };
      setMessages(prev => [...prev, userMessage]);

      // Send message to agent
      const response = await agentService.sendMessage(agent.id, {
        message,
        type,
        attachments,
      });

      // Add agent response to chat
      const agentMessage = {
        id: Date.now().toString(),
        type: response.type,
        content: response.content,
        sender: 'agent',
        timestamp: new Date().toISOString(),
      };
      setMessages(prev => [...prev, agentMessage]);

      // Clear attachments after successful send
      setAttachments([]);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleFileUpload = (event) => {
    const files = Array.from(event.target.files);
    setAttachments(prev => [...prev, ...files]);
  };

  const getAgentColor = (type) => {
    switch (type) {
      case 'code':
        return '#3b82f6';
      case 'data':
        return '#10b981';
      case 'document':
        return '#f59e0b';
      case 'language':
        return '#8b5cf6';
      default:
        return '#64748b';
    }
  };

  return (
    <ChatContainer>
      <ChatHeader>
        <AgentInfo>
          <AgentAvatar color={getAgentColor(agent.type)}>
            {agent.name[0]}
          </AgentAvatar>
          <AgentDetails>
            <AgentName>{agent.name}</AgentName>
            <AgentStatus>Online</AgentStatus>
          </AgentDetails>
        </AgentInfo>

        <FileUpload>
          <FileInput
            type="file"
            id="file-upload"
            multiple
            onChange={handleFileUpload}
          />
          <UploadButton as="label" htmlFor="file-upload">
            <FaPaperclip />
            Attach Files
          </UploadButton>
        </FileUpload>
      </ChatHeader>

      {error && (
        <ErrorMessage>
          <FaExclamationTriangle />
          {error}
        </ErrorMessage>
      )}

      <ChatInterface
        messages={messages}
        onSendMessage={handleSendMessage}
        loading={loading}
        attachments={attachments}
        onRemoveAttachment={(index) => {
          setAttachments(prev => prev.filter((_, i) => i !== index));
        }}
      />

      <div ref={messagesEndRef} />
    </ChatContainer>
  );
};

AgentChatPage.propTypes = {
  agent: PropTypes.shape({
    id: PropTypes.string.isRequired,
    name: PropTypes.string.isRequired,
    type: PropTypes.string.isRequired,
    description: PropTypes.string.isRequired,
    capabilities: PropTypes.arrayOf(PropTypes.string).isRequired,
  }).isRequired,
};

export default AgentChatPage; 