import React, { useState, useRef, useEffect } from 'react';
import styled from 'styled-components';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';
import { FaCode, FaDiagramProject, FaCheckCircle, FaFile, FaBookmark, FaSearch, FaFilter } from 'react-icons/fa';

const ChatContainer = styled.div`
  display: flex;
  flex-direction: column;
  height: 100%;
  background: ${props => props.theme.background};
  border-radius: 8px;
  overflow: hidden;
`;

const ChatHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  border-bottom: 1px solid ${props => props.theme.border};
  background: ${props => props.theme.headerBackground};
`;

const SearchBar = styled.div`
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  background: ${props => props.theme.inputBackground};
  border-radius: 20px;
  width: 300px;

  input {
    border: none;
    background: none;
    color: ${props => props.theme.text};
    width: 100%;
    font-size: 14px;

    &:focus {
      outline: none;
    }
  }
`;

const MessageList = styled.div`
  flex: 1;
  overflow-y: auto;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 16px;
`;

const MessageContainer = styled.div`
  display: flex;
  gap: 12px;
  padding: 12px;
  border-radius: 8px;
  background: ${props => props.theme.messageBackground};
  transition: all 0.2s ease;

  &:hover {
    background: ${props => props.theme.messageHoverBackground};
  }
`;

const Avatar = styled.div`
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: ${props => props.color};
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: 600;
  position: relative;
`;

const RoleBadge = styled.div`
  position: absolute;
  bottom: -4px;
  right: -4px;
  background: ${props => props.color};
  color: white;
  font-size: 10px;
  padding: 2px 6px;
  border-radius: 10px;
  border: 2px solid ${props => props.theme.background};
`;

const MessageContent = styled.div`
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 4px;
`;

const MessageHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
`;

const AgentName = styled.span`
  font-weight: 600;
  color: ${props => props.theme.text};
`;

const Timestamp = styled.span`
  font-size: 12px;
  color: ${props => props.theme.metaText};
`;

const MessageBody = styled.div`
  color: ${props => props.theme.text};
  font-size: 14px;
  line-height: 1.5;
`;

const CodeBlock = styled.div`
  margin: 8px 0;
  border-radius: 4px;
  overflow: hidden;
  background: ${props => props.theme.codeBackground};
`;

const DiagramContainer = styled.div`
  margin: 8px 0;
  padding: 12px;
  background: ${props => props.theme.diagramBackground};
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s ease;

  &:hover {
    transform: scale(1.02);
  }
`;

const DecisionPoint = styled.div`
  margin: 8px 0;
  padding: 12px;
  background: ${props => props.theme.decisionBackground};
  border-radius: 4px;
  border-left: 4px solid ${props => props.theme.primary};
`;

const VoteButton = styled.button`
  padding: 4px 8px;
  border: none;
  border-radius: 4px;
  background: ${props => props.theme.buttonBackground};
  color: ${props => props.theme.buttonText};
  cursor: pointer;
  font-size: 12px;
  transition: all 0.2s ease;

  &:hover {
    background: ${props => props.theme.buttonHoverBackground};
  }
`;

const FileReference = styled.div`
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px;
  background: ${props => props.theme.fileBackground};
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s ease;

  &:hover {
    background: ${props => props.theme.fileHoverBackground};
  }
`;

const MessageActions = styled.div`
  display: flex;
  gap: 8px;
  margin-top: 4px;
`;

const ActionButton = styled.button`
  padding: 4px;
  border: none;
  background: none;
  color: ${props => props.theme.metaText};
  cursor: pointer;
  border-radius: 4px;
  transition: all 0.2s ease;

  &:hover {
    background: ${props => props.theme.actionHoverBackground};
    color: ${props => props.theme.primary};
  }
`;

const ThreadIndicator = styled.div`
  display: flex;
  align-items: center;
  gap: 4px;
  color: ${props => props.theme.metaText};
  font-size: 12px;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 4px;
  transition: all 0.2s ease;

  &:hover {
    background: ${props => props.theme.actionHoverBackground};
  }
`;

const ChatPanel = () => {
  const [messages, setMessages] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [activeThread, setActiveThread] = useState(null);
  const messageListRef = useRef(null);

  useEffect(() => {
    // Scroll to bottom when new messages arrive
    if (messageListRef.current) {
      messageListRef.current.scrollTop = messageListRef.current.scrollHeight;
    }
  }, [messages]);

  const renderMessage = (message) => {
    const {
      id,
      agent,
      content,
      timestamp,
      type,
      threadId,
      reactions,
      votes
    } = message;

    return (
      <MessageContainer key={id}>
        <Avatar color={agent.color}>
          {agent.name[0]}
          <RoleBadge color={agent.roleColor}>{agent.role}</RoleBadge>
        </Avatar>
        <MessageContent>
          <MessageHeader>
            <AgentName>{agent.name}</AgentName>
            <Timestamp>{new Date(timestamp).toLocaleTimeString()}</Timestamp>
          </MessageHeader>
          <MessageBody>
            {type === 'code' ? (
              <CodeBlock>
                <SyntaxHighlighter language={content.language} style={vscDarkPlus}>
                  {content.code}
                </SyntaxHighlighter>
              </CodeBlock>
            ) : type === 'diagram' ? (
              <DiagramContainer>
                <FaDiagramProject />
                <span>{content.title}</span>
              </DiagramContainer>
            ) : type === 'decision' ? (
              <DecisionPoint>
                <h4>{content.question}</h4>
                <p>{content.description}</p>
                <div style={{ display: 'flex', gap: '8px', marginTop: '8px' }}>
                  <VoteButton>Approve</VoteButton>
                  <VoteButton>Reject</VoteButton>
                </div>
              </DecisionPoint>
            ) : type === 'file' ? (
              <FileReference>
                <FaFile />
                <span>{content.name}</span>
              </FileReference>
            ) : (
              content
            )}
          </MessageBody>
          <MessageActions>
            {threadId && (
              <ThreadIndicator>
                <span>Thread</span>
                <span>{threadId}</span>
              </ThreadIndicator>
            )}
            <ActionButton>
              <FaBookmark />
            </ActionButton>
            {reactions && (
              <div style={{ display: 'flex', gap: '4px' }}>
                {reactions.map((reaction) => (
                  <span key={reaction.emoji}>{reaction.emoji}</span>
                ))}
              </div>
            )}
          </MessageActions>
        </MessageContent>
      </MessageContainer>
    );
  };

  return (
    <ChatContainer>
      <ChatHeader>
        <SearchBar>
          <FaSearch />
          <input
            type="text"
            placeholder="Search messages..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </SearchBar>
        <ActionButton>
          <FaFilter />
        </ActionButton>
      </ChatHeader>
      <MessageList ref={messageListRef}>
        {messages.map(renderMessage)}
      </MessageList>
    </ChatContainer>
  );
};

export default ChatPanel; 