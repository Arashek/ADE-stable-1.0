import React, { useState } from 'react';
import styled from 'styled-components';
import { FaExclamationTriangle, FaChartLine, FaPlus, FaFilter, FaUser, FaClock } from 'react-icons/fa';

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

const RiskMetrics = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 16px;
`;

const MetricCard = styled.div`
  background: ${props => props.theme.background};
  padding: 16px;
  border-radius: 6px;
  display: flex;
  flex-direction: column;
  gap: 8px;
`;

const MetricTitle = styled.div`
  color: ${props => props.theme.metaText};
  font-size: 12px;
  display: flex;
  align-items: center;
  gap: 4px;
`;

const MetricValue = styled.div`
  color: ${props => props.theme.text};
  font-size: 24px;
  font-weight: 600;
`;

const RiskList = styled.div`
  display: flex;
  flex-direction: column;
  gap: 16px;
  overflow-y: auto;
  flex: 1;
`;

const RiskItem = styled.div`
  background: ${props => props.theme.background};
  border-radius: 6px;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  border-left: 4px solid ${props => {
    switch (props.severity) {
      case 'high': return props.theme.error;
      case 'medium': return props.theme.warning;
      case 'low': return props.theme.success;
      default: return props.theme.metaText;
    }
  }};
`;

const RiskHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
`;

const RiskTitle = styled.div`
  font-weight: 500;
  color: ${props => props.theme.text};
  display: flex;
  align-items: center;
  gap: 8px;
`;

const RiskSeverity = styled.div`
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: ${props => {
    switch (props.severity) {
      case 'high': return props.theme.error;
      case 'medium': return props.theme.warning;
      case 'low': return props.theme.success;
      default: return props.theme.metaText;
    }
  }};
`;

const RiskDescription = styled.div`
  color: ${props => props.theme.metaText};
  font-size: 14px;
  line-height: 1.5;
`;

const RiskDetails = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 12px;
  font-size: 12px;
  color: ${props => props.theme.metaText};
`;

const DetailItem = styled.div`
  display: flex;
  align-items: center;
  gap: 4px;
`;

const MitigationPlan = styled.div`
  background: ${props => props.theme.cardBackground};
  padding: 12px;
  border-radius: 4px;
  font-size: 12px;
`;

const RiskAssessmentPanel = () => {
  const [risks] = useState([
    {
      id: 1,
      title: 'Resource Allocation Bottleneck',
      description: 'Frontend team is currently overloaded with multiple high-priority tasks, which may lead to delays in critical features.',
      severity: 'high',
      probability: '70%',
      impact: 'High',
      status: 'active',
      mitigation: 'Reallocate resources from backend team and consider hiring additional frontend developers.',
      owner: 'John Doe',
      dueDate: '2024-03-15'
    },
    {
      id: 2,
      title: 'Integration Testing Delays',
      description: 'Integration testing phase is behind schedule due to incomplete API documentation and delayed backend features.',
      severity: 'medium',
      probability: '60%',
      impact: 'Medium',
      status: 'active',
      mitigation: 'Accelerate API documentation and prioritize critical backend features for testing.',
      owner: 'Jane Smith',
      dueDate: '2024-03-20'
    },
    {
      id: 3,
      title: 'Security Compliance',
      description: 'Need to ensure all new features meet security compliance requirements before deployment.',
      severity: 'high',
      probability: '40%',
      impact: 'High',
      status: 'active',
      mitigation: 'Schedule security review sessions and implement automated security testing.',
      owner: 'Mike Johnson',
      dueDate: '2024-03-25'
    }
  ]);

  const getSeverityIcon = (severity) => {
    switch (severity) {
      case 'high':
        return <FaExclamationTriangle style={{ color: '#F44336' }} />;
      case 'medium':
        return <FaExclamationTriangle style={{ color: '#FFC107' }} />;
      case 'low':
        return <FaExclamationTriangle style={{ color: '#4CAF50' }} />;
      default:
        return <FaExclamationTriangle />;
    }
  };

  return (
    <Container>
      <Header>
        <Title>
          <FaExclamationTriangle />
          Risk Assessment
        </Title>
        <Controls>
          <ControlButton>
            <FaPlus /> Add Risk
          </ControlButton>
          <ControlButton>
            <FaFilter /> Filter
          </ControlButton>
        </Controls>
      </Header>

      <RiskMetrics>
        <MetricCard>
          <MetricTitle>
            <FaExclamationTriangle />
            Active Risks
          </MetricTitle>
          <MetricValue>{risks.length}</MetricValue>
        </MetricCard>
        <MetricCard>
          <MetricTitle>
            <FaChartLine />
            High Severity
          </MetricTitle>
          <MetricValue>
            {risks.filter(risk => risk.severity === 'high').length}
          </MetricValue>
        </MetricCard>
        <MetricCard>
          <MetricTitle>
            <FaChartLine />
            Medium Severity
          </MetricTitle>
          <MetricValue>
            {risks.filter(risk => risk.severity === 'medium').length}
          </MetricValue>
        </MetricCard>
        <MetricCard>
          <MetricTitle>
            <FaChartLine />
            Low Severity
          </MetricTitle>
          <MetricValue>
            {risks.filter(risk => risk.severity === 'low').length}
          </MetricValue>
        </MetricCard>
      </RiskMetrics>

      <RiskList>
        {risks.map(risk => (
          <RiskItem key={risk.id} severity={risk.severity}>
            <RiskHeader>
              <RiskTitle>
                {getSeverityIcon(risk.severity)}
                {risk.title}
              </RiskTitle>
              <RiskSeverity severity={risk.severity}>
                {risk.severity.toUpperCase()}
              </RiskSeverity>
            </RiskHeader>

            <RiskDescription>
              {risk.description}
            </RiskDescription>

            <RiskDetails>
              <DetailItem>
                <FaChartLine />
                Probability: {risk.probability}
              </DetailItem>
              <DetailItem>
                <FaExclamationTriangle />
                Impact: {risk.impact}
              </DetailItem>
              <DetailItem>
                <FaUser />
                Owner: {risk.owner}
              </DetailItem>
              <DetailItem>
                <FaClock />
                Due: {risk.dueDate}
              </DetailItem>
            </RiskDetails>

            <MitigationPlan>
              <strong>Mitigation Plan:</strong> {risk.mitigation}
            </MitigationPlan>
          </RiskItem>
        ))}
      </RiskList>
    </Container>
  );
};

export default RiskAssessmentPanel; 