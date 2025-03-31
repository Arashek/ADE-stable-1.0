import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { FaRobot, FaSearch, FaExclamationTriangle } from 'react-icons/fa';
import { agentService } from '../../services/agentService';
import AgentList from './AgentList';
import AgentChatPage from './AgentChatPage';

const PageContainer = styled.div`
  display: flex;
  height: calc(100vh - 64px); // Adjust based on your header height
`;

const MainContent = styled.div`
  flex: 1;
  display: flex;
  flex-direction: column;
  background: white;
  border-radius: 8px;
  margin: 24px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  overflow: hidden;
`;

const Header = styled.div`
  padding: 24px;
  border-bottom: 1px solid #e2e8f0;
  display: flex;
  justify-content: space-between;
  align-items: center;
`;

const Title = styled.h1`
  font-size: 24px;
  color: #1e293b;
  margin: 0;
  display: flex;
  align-items: center;
  gap: 12px;
`;

const SearchBar = styled.div`
  display: flex;
  align-items: center;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  padding: 8px 12px;
  width: 300px;
`;

const SearchInput = styled.input`
  border: none;
  outline: none;
  background: none;
  width: 100%;
  margin-left: 8px;
  font-size: 14px;
`;

const Content = styled.div`
  flex: 1;
  display: flex;
  overflow: hidden;
`;

const WelcomeMessage = styled.div`
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  padding: 48px;
  text-align: center;
  color: #64748b;
`;

const WelcomeTitle = styled.h2`
  font-size: 28px;
  color: #1e293b;
  margin-bottom: 16px;
`;

const WelcomeText = styled.p`
  font-size: 16px;
  max-width: 600px;
  line-height: 1.6;
`;

const ErrorMessage = styled.div`
  display: flex;
  align-items: center;
  gap: 8px;
  background: #fee2e2;
  color: #991b1b;
  padding: 16px;
  border-radius: 6px;
  margin: 24px;
`;

const AgentsPage = () => {
  const [agents, setAgents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedAgent, setSelectedAgent] = useState(null);

  useEffect(() => {
    fetchAgents();
  }, []);

  const fetchAgents = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await agentService.getAgents();
      setAgents(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const filteredAgents = agents.filter(agent =>
    agent.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    agent.description.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <PageContainer>
      <AgentList
        agents={filteredAgents}
        selectedAgent={selectedAgent}
        onAgentSelect={setSelectedAgent}
      />
      <MainContent>
        <Header>
          <Title>
            <FaRobot />
            AI Agents
          </Title>
          <SearchBar>
            <FaSearch color="#64748b" />
            <SearchInput
              type="text"
              placeholder="Search agents..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
          </SearchBar>
        </Header>

        <Content>
          {error && (
            <ErrorMessage>
              <FaExclamationTriangle />
              {error}
            </ErrorMessage>
          )}

          {selectedAgent ? (
            <AgentChatPage agent={selectedAgent} />
          ) : (
            <WelcomeMessage>
              <WelcomeTitle>Welcome to AI Agents</WelcomeTitle>
              <WelcomeText>
                Select an agent from the sidebar to start a conversation. Each agent is specialized
                in different areas and can help you with various tasks.
              </WelcomeText>
            </WelcomeMessage>
          )}
        </Content>
      </MainContent>
    </PageContainer>
  );
};

export default AgentsPage; 