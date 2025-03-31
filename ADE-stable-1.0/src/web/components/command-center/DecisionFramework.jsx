import React, { useState } from 'react';
import styled from 'styled-components';
import { 
  FaCheckCircle, FaTimesCircle, FaChartBar, FaHistory, 
  FaThumbsUp, FaThumbsDown, FaComments, FaArrowRight,
  FaExclamationTriangle, FaCheck, FaTimes
} from 'react-icons/fa';

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

const Content = styled.div`
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 20px;
  flex: 1;
  overflow: hidden;
`;

const MainPanel = styled.div`
  background: ${props => props.theme.background};
  border-radius: 6px;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 16px;
`;

const DecisionPoint = styled.div`
  background: ${props => props.theme.cardBackground};
  border-radius: 6px;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;
`;

const DecisionTitle = styled.h4`
  color: ${props => props.theme.text};
  margin: 0;
  display: flex;
  align-items: center;
  gap: 8px;
`;

const DecisionDescription = styled.div`
  color: ${props => props.theme.metaText};
  font-size: 14px;
  line-height: 1.5;
`;

const OptionsList = styled.div`
  display: flex;
  flex-direction: column;
  gap: 12px;
`;

const OptionCard = styled.div`
  background: ${props => props.theme.background};
  border-radius: 6px;
  padding: 12px;
  display: flex;
  flex-direction: column;
  gap: 8px;
  border: 1px solid ${props => props.theme.border};

  &:hover {
    border-color: ${props => props.theme.primary};
  }
`;

const OptionHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
`;

const OptionTitle = styled.div`
  font-weight: 500;
  color: ${props => props.theme.text};
`;

const OptionVotes = styled.div`
  display: flex;
  align-items: center;
  gap: 8px;
`;

const VoteButton = styled.button`
  padding: 4px 8px;
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

const ProsCons = styled.div`
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
`;

const ProsConsList = styled.div`
  display: flex;
  flex-direction: column;
  gap: 4px;
`;

const ProsConsItem = styled.div`
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: ${props => props.theme.metaText};
`;

const SidePanel = styled.div`
  background: ${props => props.theme.background};
  border-radius: 6px;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 16px;
`;

const ImpactAnalysis = styled.div`
  display: flex;
  flex-direction: column;
  gap: 12px;
`;

const ImpactMetric = styled.div`
  display: flex;
  flex-direction: column;
  gap: 4px;
`;

const MetricLabel = styled.div`
  font-size: 12px;
  color: ${props => props.theme.metaText};
`;

const MetricBar = styled.div`
  height: 8px;
  background: ${props => props.theme.border};
  border-radius: 4px;
  overflow: hidden;
`;

const MetricFill = styled.div`
  height: 100%;
  background: ${props => props.theme.primary};
  width: ${props => props.value}%;
  transition: width 0.3s ease;
`;

const DecisionHistory = styled.div`
  display: flex;
  flex-direction: column;
  gap: 8px;
  overflow-y: auto;
  flex: 1;
`;

const HistoryItem = styled.div`
  background: ${props => props.theme.cardBackground};
  border-radius: 4px;
  padding: 8px;
  font-size: 12px;
  color: ${props => props.theme.metaText};
`;

const DecisionFramework = () => {
  const [currentDecision] = useState({
    id: 1,
    title: 'Database Technology Selection',
    description: 'Choose the primary database technology for the new microservices architecture',
    options: [
      {
        id: 1,
        title: 'PostgreSQL',
        description: 'Traditional relational database with strong consistency and ACID compliance',
        pros: ['Strong consistency', 'ACID compliance', 'Mature ecosystem'],
        cons: ['Less flexible schema', 'Limited horizontal scaling'],
        votes: { up: 8, down: 2 }
      },
      {
        id: 2,
        title: 'MongoDB',
        description: 'Document-based NoSQL database with flexible schema and horizontal scaling',
        pros: ['Flexible schema', 'Horizontal scaling', 'JSON support'],
        cons: ['Eventually consistent', 'Complex transactions'],
        votes: { up: 5, down: 3 }
      }
    ],
    impact: {
      performance: 75,
      scalability: 85,
      maintainability: 65,
      cost: 45
    }
  });

  const [decisionHistory] = useState([
    {
      id: 1,
      date: '2024-03-10',
      title: 'API Gateway Selection',
      decision: 'Selected Kong Gateway',
      rationale: 'Best balance of features and performance'
    },
    {
      id: 2,
      date: '2024-03-08',
      title: 'Authentication Method',
      decision: 'OAuth 2.0 with JWT',
      rationale: 'Industry standard with good security'
    }
  ]);

  return (
    <Container>
      <Header>
        <Title>
          <FaChartBar />
          Decision Framework
        </Title>
        <Controls>
          <ControlButton>
            <FaHistory /> History
          </ControlButton>
          <ControlButton>
            <FaComments /> Discussion
          </ControlButton>
        </Controls>
      </Header>

      <Content>
        <MainPanel>
          <DecisionPoint>
            <DecisionTitle>
              <FaExclamationTriangle />
              {currentDecision.title}
            </DecisionTitle>
            <DecisionDescription>
              {currentDecision.description}
            </DecisionDescription>

            <OptionsList>
              {currentDecision.options.map(option => (
                <OptionCard key={option.id}>
                  <OptionHeader>
                    <OptionTitle>{option.title}</OptionTitle>
                    <OptionVotes>
                      <VoteButton>
                        <FaThumbsUp />
                        {option.votes.up}
                      </VoteButton>
                      <VoteButton>
                        <FaThumbsDown />
                        {option.votes.down}
                      </VoteButton>
                    </OptionVotes>
                  </OptionHeader>
                  <DecisionDescription>
                    {option.description}
                  </DecisionDescription>
                  <ProsCons>
                    <ProsConsList>
                      <ProsConsItem>
                        <FaCheck style={{ color: '#4CAF50' }} />
                        Pros
                      </ProsConsItem>
                      {option.pros.map(pro => (
                        <ProsConsItem key={pro}>
                          <FaArrowRight />
                          {pro}
                        </ProsConsItem>
                      ))}
                    </ProsConsList>
                    <ProsConsList>
                      <ProsConsItem>
                        <FaTimes style={{ color: '#F44336' }} />
                        Cons
                      </ProsConsItem>
                      {option.cons.map(con => (
                        <ProsConsItem key={con}>
                          <FaArrowRight />
                          {con}
                        </ProsConsItem>
                      ))}
                    </ProsConsList>
                  </ProsCons>
                </OptionCard>
              ))}
            </OptionsList>
          </DecisionPoint>
        </MainPanel>

        <SidePanel>
          <ImpactAnalysis>
            <Title>Impact Analysis</Title>
            <ImpactMetric>
              <MetricLabel>Performance</MetricLabel>
              <MetricBar>
                <MetricFill value={currentDecision.impact.performance} />
              </MetricBar>
            </ImpactMetric>
            <ImpactMetric>
              <MetricLabel>Scalability</MetricLabel>
              <MetricBar>
                <MetricFill value={currentDecision.impact.scalability} />
              </MetricBar>
            </ImpactMetric>
            <ImpactMetric>
              <MetricLabel>Maintainability</MetricLabel>
              <MetricBar>
                <MetricFill value={currentDecision.impact.maintainability} />
              </MetricBar>
            </ImpactMetric>
            <ImpactMetric>
              <MetricLabel>Cost</MetricLabel>
              <MetricBar>
                <MetricFill value={currentDecision.impact.cost} />
              </MetricBar>
            </ImpactMetric>
          </ImpactAnalysis>

          <DecisionHistory>
            <Title>Decision History</Title>
            {decisionHistory.map(decision => (
              <HistoryItem key={decision.id}>
                <div>{decision.date}</div>
                <div><strong>{decision.title}</strong></div>
                <div>Decision: {decision.decision}</div>
                <div>Rationale: {decision.rationale}</div>
              </HistoryItem>
            ))}
          </DecisionHistory>
        </SidePanel>
      </Content>
    </Container>
  );
};

export default DecisionFramework; 