import React, { useState } from 'react';
import styled from 'styled-components';
import { FaPlus, FaSearch, FaFilter, FaEllipsisV, FaMicrochip, FaClock, FaCheck } from 'react-icons/fa';

const AgentsContainer = styled.div`
  display: flex;
  flex-direction: column;
  gap: 24px;
`;

const Header = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
`;

const Title = styled.h1`
  font-size: 24px;
  color: #1e293b;
`;

const ActionButton = styled.button`
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  background: #3b82f6;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: background-color 0.2s;

  &:hover {
    background: #2563eb;
  }
`;

const SearchBar = styled.div`
  display: flex;
  align-items: center;
  gap: 12px;
  background: white;
  padding: 8px 16px;
  border-radius: 6px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
`;

const SearchInput = styled.input`
  border: none;
  outline: none;
  font-size: 14px;
  width: 100%;
`;

const AgentsGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
`;

const AgentCard = styled.div`
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
`;

const AgentHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 16px;
`;

const AgentTitle = styled.h3`
  font-size: 18px;
  color: #1e293b;
  margin: 0;
`;

const AgentMenu = styled.button`
  background: none;
  border: none;
  color: #64748b;
  cursor: pointer;
  padding: 4px;
  border-radius: 4px;

  &:hover {
    background: #f1f5f9;
  }
`;

const AgentInfo = styled.div`
  display: flex;
  flex-direction: column;
  gap: 12px;
`;

const InfoRow = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
`;

const InfoLabel = styled.span`
  color: #64748b;
  font-size: 14px;
`;

const InfoValue = styled.span`
  color: #1e293b;
  font-size: 14px;
`;

const StatusBadge = styled.span`
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
  background: ${props => props.active ? '#dcfce7' : '#fee2e2'};
  color: ${props => props.active ? '#166534' : '#991b1b'};
`;

const CapabilityList = styled.div`
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 12px;
`;

const Capability = styled.span`
  background: #f1f5f9;
  color: #64748b;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
`;

const agents = [
  {
    id: 1,
    name: 'CodeReviewer',
    status: 'active',
    model: 'GPT-4',
    capabilities: ['Code Review', 'Bug Detection', 'Performance Analysis'],
    tasksCompleted: 45,
    lastActive: '2 minutes ago',
  },
  {
    id: 2,
    name: 'DocumentationBot',
    status: 'inactive',
    model: 'Claude 3',
    capabilities: ['Documentation', 'API Specs', 'User Guides'],
    tasksCompleted: 28,
    lastActive: '1 hour ago',
  },
  {
    id: 3,
    name: 'TestGenerator',
    status: 'active',
    model: 'GPT-4',
    capabilities: ['Unit Tests', 'Integration Tests', 'E2E Tests'],
    tasksCompleted: 62,
    lastActive: '5 minutes ago',
  },
];

const Agents = () => {
  const [searchQuery, setSearchQuery] = useState('');

  return (
    <AgentsContainer>
      <Header>
        <Title>AI Agents</Title>
        <ActionButton>
          <FaPlus />
          New Agent
        </ActionButton>
      </Header>

      <SearchBar>
        <FaSearch color="#64748b" />
        <SearchInput
          placeholder="Search agents..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
        />
        <FaFilter color="#64748b" />
      </SearchBar>

      <AgentsGrid>
        {agents.map((agent) => (
          <AgentCard key={agent.id}>
            <AgentHeader>
              <AgentTitle>{agent.name}</AgentTitle>
              <AgentMenu>
                <FaEllipsisV />
              </AgentMenu>
            </AgentHeader>

            <AgentInfo>
              <InfoRow>
                <InfoLabel>Status</InfoLabel>
                <StatusBadge active={agent.status === 'active'}>
                  {agent.status === 'active' ? 'Active' : 'Inactive'}
                </StatusBadge>
              </InfoRow>

              <InfoRow>
                <InfoLabel>Model</InfoLabel>
                <InfoValue>
                  <FaMicrochip style={{ marginRight: '4px' }} />
                  {agent.model}
                </InfoValue>
              </InfoRow>

              <InfoRow>
                <InfoLabel>Tasks Completed</InfoLabel>
                <InfoValue>
                  <FaCheck style={{ marginRight: '4px' }} />
                  {agent.tasksCompleted}
                </InfoValue>
              </InfoRow>

              <InfoRow>
                <InfoLabel>Last Active</InfoLabel>
                <InfoValue>
                  <FaClock style={{ marginRight: '4px' }} />
                  {agent.lastActive}
                </InfoValue>
              </InfoRow>

              <CapabilityList>
                {agent.capabilities.map((capability, index) => (
                  <Capability key={index}>{capability}</Capability>
                ))}
              </CapabilityList>
            </AgentInfo>
          </AgentCard>
        ))}
      </AgentsGrid>
    </AgentsContainer>
  );
};

export default Agents; 