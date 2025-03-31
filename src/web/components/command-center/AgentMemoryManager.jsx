import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { 
  FaBrain, FaHistory, FaSearch, FaFilter, FaTimes,
  FaCode, FaFileAlt, FaImage, FaLink, FaComments,
  FaSync, FaExclamationTriangle, FaCheckCircle
} from 'react-icons/fa';
import SyntaxHighlighter from 'react-syntax-highlighter';
import { docco } from 'react-syntax-highlighter/dist/esm/styles/hljs';

const Container = styled.div`
  background: ${props => props.theme.cardBackground};
  border-radius: 8px;
  padding: 20px;
  height: 100%;
  display: flex;
  flex-direction: column;
  gap: 20px;
`;

const Header = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
`;

const Title = styled.h3`
  color: ${props => props.theme.text};
  margin: 0;
  display: flex;
  align-items: center;
  gap: 8px;
`;

const Controls = styled.div`
  display: flex;
  gap: 8px;
`;

const ControlButton = styled.button`
  padding: 6px 12px;
  border: none;
  border-radius: 4px;
  background: ${props => props.theme.buttonBackground};
  color: ${props => props.theme.text};
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 4px;
  transition: all 0.2s ease;

  &:hover {
    background: ${props => props.theme.buttonHoverBackground};
  }
`;

const SearchBar = styled.div`
  display: flex;
  gap: 8px;
  align-items: center;
`;

const SearchInput = styled.input`
  flex: 1;
  padding: 8px 12px;
  border: 1px solid ${props => props.theme.border};
  border-radius: 4px;
  background: ${props => props.theme.background};
  color: ${props => props.theme.text};

  &:focus {
    outline: none;
    border-color: ${props => props.theme.primary};
  }
`;

const FilterSelect = styled.select`
  padding: 8px 12px;
  border: 1px solid ${props => props.theme.border};
  border-radius: 4px;
  background: ${props => props.theme.background};
  color: ${props => props.theme.text};
`;

const Content = styled.div`
  display: grid;
  grid-template-columns: 1fr 2fr;
  gap: 20px;
  flex: 1;
  overflow: hidden;
`;

const AgentList = styled.div`
  display: flex;
  flex-direction: column;
  gap: 12px;
  overflow-y: auto;
  flex: 1;
`;

const AgentCard = styled.div`
  background: ${props => props.theme.cardBackground};
  border-radius: 6px;
  padding: 12px;
  display: flex;
  flex-direction: column;
  gap: 8px;
  cursor: pointer;
  border: 1px solid ${props => props.theme.border};

  &:hover {
    border-color: ${props => props.theme.primary};
  }
`;

const AgentHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
`;

const AgentTitle = styled.div`
  font-weight: 500;
  color: ${props => props.theme.text};
  display: flex;
  align-items: center;
  gap: 8px;
`;

const AgentMeta = styled.div`
  font-size: 12px;
  color: ${props => props.theme.metaText};
`;

const EventList = styled.div`
  display: flex;
  flex-direction: column;
  gap: 8px;
  overflow-y: auto;
  max-height: 200px;
`;

const EventItem = styled.div`
  background: ${props => props.theme.cardBackground};
  border-radius: 4px;
  padding: 8px;
  font-size: 12px;
  color: ${props => props.theme.metaText};
  display: flex;
  justify-content: space-between;
  align-items: center;
`;

const DetailsPanel = styled.div`
  background: ${props => props.theme.background};
  border-radius: 6px;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 16px;
`;

const DetailsHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
`;

const DetailsTitle = styled.h4`
  color: ${props => props.theme.text};
  margin: 0;
`;

const DetailsContent = styled.div`
  flex: 1;
  overflow-y: auto;
  font-size: 14px;
  line-height: 1.5;
  color: ${props => props.theme.text};
`;

const StatusIndicator = styled.div`
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: ${props => props.theme.metaText};
`;

const AgentMemoryManager = () => {
  const [agents, setAgents] = useState([
    {
      id: '1',
      name: 'Code Maintainer',
      accessLevel: 'full_access',
      lastSync: new Date(),
      syncFrequency: 300,
      isActive: true,
      events: [
        {
          id: '1',
          type: 'code_change',
          timestamp: new Date(),
          details: 'Updated API endpoint',
          affectedFiles: ['src/api/main.py'],
          priority: 1
        }
      ]
    },
    {
      id: '2',
      name: 'Documentation Agent',
      accessLevel: 'read_write',
      lastSync: new Date(),
      syncFrequency: 600,
      isActive: true,
      events: [
        {
          id: '2',
          type: 'documentation_update',
          timestamp: new Date(),
          details: 'Updated API documentation',
          affectedFiles: ['docs/api.md'],
          priority: 2
        }
      ]
    }
  ]);

  const [searchQuery, setSearchQuery] = useState('');
  const [filterType, setFilterType] = useState('all');
  const [selectedAgent, setSelectedAgent] = useState(null);

  const filteredAgents = agents.filter(agent => {
    const matchesSearch = agent.name.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesFilter = filterType === 'all' || agent.accessLevel === filterType;
    return matchesSearch && matchesFilter;
  });

  const renderEventDetails = (event) => {
    if (!event) return null;

    switch (event.type) {
      case 'code_change':
        return (
          <div>
            <h5>Code Change Details</h5>
            <p>Files affected: {event.affectedFiles.join(', ')}</p>
            <p>Changes: {event.details}</p>
          </div>
        );
      case 'documentation_update':
        return (
          <div>
            <h5>Documentation Update</h5>
            <p>Files affected: {event.affectedFiles.join(', ')}</p>
            <p>Updates: {event.details}</p>
          </div>
        );
      default:
        return <div>{event.details}</div>;
    }
  };

  const syncAgentMemory = (agentId) => {
    // Implementation for syncing agent memory
    console.log('Syncing memory for agent:', agentId);
  };

  return (
    <Container>
      <Header>
        <Title>
          <FaBrain />
          Agent Memory Manager
        </Title>
        <Controls>
          <ControlButton>
            <FaHistory /> History
          </ControlButton>
        </Controls>
      </Header>

      <SearchBar>
        <FaSearch />
        <SearchInput
          placeholder="Search agents..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
        />
        <FilterSelect
          value={filterType}
          onChange={(e) => setFilterType(e.target.value)}
        >
          <option value="all">All Access Levels</option>
          <option value="read_only">Read Only</option>
          <option value="read_write">Read Write</option>
          <option value="full_access">Full Access</option>
        </FilterSelect>
      </SearchBar>

      <Content>
        <AgentList>
          {filteredAgents.map(agent => (
            <AgentCard
              key={agent.id}
              onClick={() => setSelectedAgent(agent)}
            >
              <AgentHeader>
                <AgentTitle>
                  {agent.name}
                </AgentTitle>
                <StatusIndicator>
                  {agent.isActive ? (
                    <FaCheckCircle color="green" />
                  ) : (
                    <FaExclamationTriangle color="orange" />
                  )}
                  {agent.accessLevel}
                </StatusIndicator>
              </AgentHeader>
              <AgentMeta>
                Last sync: {agent.lastSync.toLocaleTimeString()}
              </AgentMeta>
              <EventList>
                {agent.events.map(event => (
                  <EventItem key={event.id}>
                    <div>
                      {event.type === 'code_change' && <FaCode />}
                      {event.type === 'documentation_update' && <FaFileAlt />}
                      {event.details}
                    </div>
                    <div>
                      {event.timestamp.toLocaleTimeString()}
                    </div>
                  </EventItem>
                ))}
              </EventList>
            </AgentCard>
          ))}
        </AgentList>

        <DetailsPanel>
          <DetailsHeader>
            <DetailsTitle>
              {selectedAgent ? selectedAgent.name : 'Select an agent to view details'}
            </DetailsTitle>
            {selectedAgent && (
              <ControlButton onClick={() => syncAgentMemory(selectedAgent.id)}>
                <FaSync /> Sync Memory
              </ControlButton>
            )}
          </DetailsHeader>
          <DetailsContent>
            {selectedAgent && (
              <div>
                <h5>Access Level</h5>
                <p>{selectedAgent.accessLevel}</p>
                
                <h5>Sync Settings</h5>
                <p>Frequency: {selectedAgent.syncFrequency} seconds</p>
                <p>Last sync: {selectedAgent.lastSync.toLocaleString()}</p>
                
                <h5>Recent Events</h5>
                {selectedAgent.events.map(event => (
                  <div key={event.id}>
                    <h6>{event.type}</h6>
                    {renderEventDetails(event)}
                  </div>
                ))}
              </div>
            )}
          </DetailsContent>
        </DetailsPanel>
      </Content>
    </Container>
  );
};

export default AgentMemoryManager; 