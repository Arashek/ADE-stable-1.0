import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { FaChartLine, FaTasks, FaProjectDiagram, FaExclamationTriangle, FaCheckCircle } from 'react-icons/fa';
import GanttChart from '../visualizations/GanttChart';
import KanbanBoard from '../visualizations/KanbanBoard';
import DependencyGraph from '../visualizations/DependencyGraph';

const DashboardContainer = styled.div`
  display: flex;
  flex-direction: column;
  height: 100%;
  background: ${props => props.theme.background};
  padding: 20px;
  gap: 20px;
`;

const Header = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
`;

const Title = styled.h2`
  color: ${props => props.theme.text};
  margin: 0;
`;

const ViewControls = styled.div`
  display: flex;
  gap: 10px;
`;

const ViewButton = styled.button`
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  background: ${props => props.active ? props.theme.primary : props.theme.buttonBackground};
  color: ${props => props.active ? props.theme.buttonText : props.theme.text};
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.2s ease;

  &:hover {
    background: ${props => props.theme.buttonHoverBackground};
  }
`;

const MetricsGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
  margin-bottom: 20px;
`;

const MetricCard = styled.div`
  background: ${props => props.theme.cardBackground};
  padding: 16px;
  border-radius: 8px;
  display: flex;
  flex-direction: column;
  gap: 8px;
`;

const MetricTitle = styled.div`
  color: ${props => props.theme.metaText};
  font-size: 14px;
`;

const MetricValue = styled.div`
  color: ${props => props.theme.text};
  font-size: 24px;
  font-weight: 600;
`;

const MetricTrend = styled.div`
  display: flex;
  align-items: center;
  gap: 4px;
  color: ${props => props.trend === 'up' ? props.theme.success : props.theme.error};
  font-size: 12px;
`;

const VisualizationContainer = styled.div`
  flex: 1;
  background: ${props => props.theme.cardBackground};
  border-radius: 8px;
  padding: 16px;
  min-height: 400px;
`;

const RiskSection = styled.div`
  background: ${props => props.theme.warningBackground};
  border-radius: 8px;
  padding: 16px;
  margin-top: 20px;
`;

const RiskHeader = styled.div`
  display: flex;
  align-items: center;
  gap: 8px;
  color: ${props => props.theme.warning};
  margin-bottom: 12px;
`;

const RiskList = styled.div`
  display: flex;
  flex-direction: column;
  gap: 8px;
`;

const RiskItem = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px;
  background: ${props => props.theme.background};
  border-radius: 4px;
`;

const ProjectDashboard = () => {
  const [view, setView] = useState('gantt');
  const [metrics, setMetrics] = useState({
    completion: { value: 65, trend: 'up' },
    velocity: { value: 12, trend: 'up' },
    blockers: { value: 3, trend: 'down' },
    resources: { value: 85, trend: 'up' }
  });
  const [risks, setRisks] = useState([
    { id: 1, description: 'Resource allocation bottleneck in frontend team', impact: 'High' },
    { id: 2, description: 'Integration testing delays', impact: 'Medium' },
    { id: 3, description: 'API documentation incomplete', impact: 'Low' }
  ]);

  const renderVisualization = () => {
    switch (view) {
      case 'gantt':
        return <GanttChart />;
      case 'kanban':
        return <KanbanBoard />;
      case 'dependencies':
        return <DependencyGraph />;
      default:
        return <GanttChart />;
    }
  };

  return (
    <DashboardContainer>
      <Header>
        <Title>Project Dashboard</Title>
        <ViewControls>
          <ViewButton
            active={view === 'gantt'}
            onClick={() => setView('gantt')}
          >
            <FaChartLine /> Timeline
          </ViewButton>
          <ViewButton
            active={view === 'kanban'}
            onClick={() => setView('kanban')}
          >
            <FaTasks /> Kanban
          </ViewButton>
          <ViewButton
            active={view === 'dependencies'}
            onClick={() => setView('dependencies')}
          >
            <FaProjectDiagram /> Dependencies
          </ViewButton>
        </ViewControls>
      </Header>

      <MetricsGrid>
        <MetricCard>
          <MetricTitle>Project Completion</MetricTitle>
          <MetricValue>{metrics.completion.value}%</MetricValue>
          <MetricTrend trend={metrics.completion.trend}>
            {metrics.completion.trend === 'up' ? '↑' : '↓'} 5% from last week
          </MetricTrend>
        </MetricCard>
        <MetricCard>
          <MetricTitle>Team Velocity</MetricTitle>
          <MetricValue>{metrics.velocity.value}</MetricValue>
          <MetricTrend trend={metrics.velocity.trend}>
            {metrics.velocity.trend === 'up' ? '↑' : '↓'} 2 points from last week
          </MetricTrend>
        </MetricCard>
        <MetricCard>
          <MetricTitle>Active Blockers</MetricTitle>
          <MetricValue>{metrics.blockers.value}</MetricValue>
          <MetricTrend trend={metrics.blockers.trend}>
            {metrics.blockers.trend === 'up' ? '↑' : '↓'} 1 from last week
          </MetricTrend>
        </MetricCard>
        <MetricCard>
          <MetricTitle>Resource Utilization</MetricTitle>
          <MetricValue>{metrics.resources.value}%</MetricValue>
          <MetricTrend trend={metrics.resources.trend}>
            {metrics.resources.trend === 'up' ? '↑' : '↓'} 3% from last week
          </MetricTrend>
        </MetricCard>
      </MetricsGrid>

      <VisualizationContainer>
        {renderVisualization()}
      </VisualizationContainer>

      <RiskSection>
        <RiskHeader>
          <FaExclamationTriangle />
          <h3>Active Risks & Blockers</h3>
        </RiskHeader>
        <RiskList>
          {risks.map(risk => (
            <RiskItem key={risk.id}>
              <div>{risk.description}</div>
              <div style={{ color: risk.impact === 'High' ? '#ff4444' : 
                          risk.impact === 'Medium' ? '#ffbb33' : '#00C851' }}>
                {risk.impact}
              </div>
            </RiskItem>
          ))}
        </RiskList>
      </RiskSection>
    </DashboardContainer>
  );
};

export default ProjectDashboard; 