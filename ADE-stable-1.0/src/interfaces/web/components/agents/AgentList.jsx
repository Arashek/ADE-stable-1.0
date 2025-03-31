import React from 'react';
import styled from 'styled-components';
import { FaRobot, FaCode, FaChartLine, FaFileAlt, FaLanguage } from 'react-icons/fa';
import PropTypes from 'prop-types';

const Sidebar = styled.div`
  width: 300px;
  background: white;
  border-right: 1px solid #e2e8f0;
  display: flex;
  flex-direction: column;
  overflow: hidden;
`;

const SidebarHeader = styled.div`
  padding: 24px;
  border-bottom: 1px solid #e2e8f0;
`;

const SidebarTitle = styled.h2`
  font-size: 18px;
  color: #1e293b;
  margin: 0;
  display: flex;
  align-items: center;
  gap: 8px;
`;

const AgentList = styled.div`
  flex: 1;
  overflow-y: auto;
  padding: 16px;
`;

const AgentCard = styled.div`
  background: ${props => props.selected ? '#f1f5f9' : 'white'};
  border: 1px solid ${props => props.selected ? '#3b82f6' : '#e2e8f0'};
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 12px;
  cursor: pointer;
  transition: all 0.2s;

  &:hover {
    border-color: #3b82f6;
    background: #f8fafc;
  }
`;

const AgentHeader = styled.div`
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 8px;
`;

const AgentIcon = styled.div`
  width: 32px;
  height: 32px;
  background: ${props => props.color};
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
`;

const AgentName = styled.h3`
  font-size: 16px;
  color: #1e293b;
  margin: 0;
`;

const AgentDescription = styled.p`
  font-size: 14px;
  color: #64748b;
  margin: 0;
  line-height: 1.5;
`;

const AgentCapabilities = styled.div`
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
  margin-top: 12px;
`;

const CapabilityTag = styled.span`
  background: #f1f5f9;
  color: #64748b;
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 12px;
`;

const getAgentIcon = (type) => {
  switch (type) {
    case 'code':
      return <FaCode />;
    case 'data':
      return <FaChartLine />;
    case 'document':
      return <FaFileAlt />;
    case 'language':
      return <FaLanguage />;
    default:
      return <FaRobot />;
  }
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

const AgentListComponent = ({ agents, selectedAgent, onAgentSelect }) => {
  return (
    <Sidebar>
      <SidebarHeader>
        <SidebarTitle>
          <FaRobot />
          Available Agents
        </SidebarTitle>
      </SidebarHeader>

      <AgentList>
        {agents.map(agent => (
          <AgentCard
            key={agent.id}
            selected={selectedAgent?.id === agent.id}
            onClick={() => onAgentSelect(agent)}
          >
            <AgentHeader>
              <AgentIcon color={getAgentColor(agent.type)}>
                {getAgentIcon(agent.type)}
              </AgentIcon>
              <AgentName>{agent.name}</AgentName>
            </AgentHeader>
            <AgentDescription>{agent.description}</AgentDescription>
            <AgentCapabilities>
              {agent.capabilities.map(capability => (
                <CapabilityTag key={capability}>{capability}</CapabilityTag>
              ))}
            </AgentCapabilities>
          </AgentCard>
        ))}
      </AgentList>
    </Sidebar>
  );
};

AgentListComponent.propTypes = {
  agents: PropTypes.arrayOf(
    PropTypes.shape({
      id: PropTypes.string.isRequired,
      name: PropTypes.string.isRequired,
      description: PropTypes.string.isRequired,
      type: PropTypes.string.isRequired,
      capabilities: PropTypes.arrayOf(PropTypes.string).isRequired,
    })
  ).isRequired,
  selectedAgent: PropTypes.shape({
    id: PropTypes.string.isRequired,
    name: PropTypes.string.isRequired,
    description: PropTypes.string.isRequired,
    type: PropTypes.string.isRequired,
    capabilities: PropTypes.arrayOf(PropTypes.string).isRequired,
  }),
  onAgentSelect: PropTypes.func.isRequired,
};

export default AgentListComponent; 