import React, { useState, useEffect, useRef } from 'react';
import styled from 'styled-components';
import { useWebSocket, subscribeToEvents, emitEvent } from '../../services/websocket';
import { colors, spacing, shadows } from '../styles';

const PanelContainer = styled.div`
  background: white;
  border-radius: 8px;
  box-shadow: ${shadows.md};
  padding: ${spacing.md};
  height: 100%;
  display: flex;
  flex-direction: column;
`;

const AgentList = styled.div`
  flex: 1;
  overflow-y: auto;
  margin-bottom: ${spacing.md};
`;

const AgentItem = styled.div`
  display: flex;
  align-items: center;
  padding: ${spacing.sm};
  border-radius: 4px;
  margin-bottom: ${spacing.sm};
  background: ${props => props.isActive ? colors.primary + '20' : 'transparent'};
  cursor: pointer;
  transition: all 0.2s ease;

  &:hover {
    background: ${colors.primary + '30'};
  }
`;

const StatusIndicator = styled.div`
  width: 8px;
  height: 8px;
  border-radius: 50%;
  margin-right: ${spacing.sm};
  background: ${props => {
    switch (props.status) {
      case 'active': return colors.success;
      case 'busy': return colors.warning;
      case 'idle': return colors.textLight;
      default: return colors.textLight;
    }
  }};
  transition: all 0.2s ease;
`;

const CommandInput = styled.div`
  display: flex;
  gap: ${spacing.sm};
  align-items: center;
`;

const Input = styled.input`
  flex: 1;
  padding: ${spacing.sm};
  border: 1px solid ${colors.border};
  border-radius: 4px;
  font-size: 14px;
  
  &:focus {
    outline: none;
    border-color: ${colors.primary};
    box-shadow: 0 0 0 2px ${colors.primary + '20'};
  }
`;

const SendButton = styled.button`
  padding: ${spacing.sm} ${spacing.md};
  background: ${colors.primary};
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s ease;

  &:hover {
    background: ${colors.primaryDark};
  }

  &:disabled {
    background: ${colors.textLight};
    cursor: not-allowed;
  }
`;

const CommandPanel = ({ onAgentSelect }) => {
  const [agents, setAgents] = useState([]);
  const [command, setCommand] = useState('');
  const [selectedAgent, setSelectedAgent] = useState(null);
  const { connect, disconnect, isConnected } = useWebSocket();
  const inputRef = useRef(null);

  useEffect(() => {
    connect();

    // Subscribe to agent updates
    const unsubscribe = subscribeToEvents((event) => {
      if (event.type === 'agent_update') {
        setAgents(prevAgents => {
          const updatedAgents = prevAgents.map(agent => 
            agent.id === event.data.id ? { ...agent, ...event.data } : agent
          );
          return updatedAgents;
        });
      }
    });

    return () => {
      unsubscribe();
      disconnect();
    };
  }, []);

  const handleCommandSubmit = (e) => {
    e.preventDefault();
    if (!command.trim()) return;

    emitEvent('command', {
      command,
      agentId: selectedAgent?.id,
      timestamp: Date.now(),
    });

    setCommand('');
    inputRef.current?.focus();
  };

  const handleAgentSelect = (agent) => {
    setSelectedAgent(agent);
    onAgentSelect?.(agent.id);
  };

  return (
    <PanelContainer>
      <AgentList>
        {agents.map(agent => (
          <AgentItem
            key={agent.id}
            isActive={selectedAgent?.id === agent.id}
            onClick={() => handleAgentSelect(agent)}
          >
            <StatusIndicator status={agent.status} />
            <div>
              <div>{agent.name}</div>
              <div style={{ fontSize: '12px', color: colors.textLight }}>
                {agent.currentTask || 'Idle'}
              </div>
            </div>
          </AgentItem>
        ))}
      </AgentList>

      <CommandInput>
        <Input
          ref={inputRef}
          type="text"
          value={command}
          onChange={(e) => setCommand(e.target.value)}
          placeholder="Type a command..."
          onSubmit={handleCommandSubmit}
        />
        <SendButton
          onClick={handleCommandSubmit}
          disabled={!command.trim() || !isConnected}
        >
          Send
        </SendButton>
      </CommandInput>
    </PanelContainer>
  );
};

export default CommandPanel; 