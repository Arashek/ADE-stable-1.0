import React from 'react';
import styled from 'styled-components';
import useClipboardManagerStore from '../../utils/clipboard-manager';

const StatsContainer = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
  padding: 16px;
  background: ${props => props.theme.background};
  border-radius: 8px;
`;

const StatCard = styled.div`
  padding: 16px;
  background: ${props => props.theme.cardBackground};
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
`;

const StatTitle = styled.h3`
  font-size: 14px;
  color: ${props => props.theme.metaText};
  margin-bottom: 8px;
`;

const StatValue = styled.div`
  font-size: 24px;
  font-weight: 600;
  color: ${props => props.theme.text};
`;

const StatSubtext = styled.div`
  font-size: 12px;
  color: ${props => props.theme.metaText};
  margin-top: 4px;
`;

const TypeDistribution = styled.div`
  display: flex;
  flex-direction: column;
  gap: 8px;
`;

const TypeBar = styled.div`
  display: flex;
  align-items: center;
  gap: 8px;
`;

const TypeLabel = styled.span`
  font-size: 12px;
  color: ${props => props.theme.text};
  min-width: 80px;
`;

const BarContainer = styled.div`
  flex: 1;
  height: 8px;
  background: ${props => props.theme.border};
  border-radius: 4px;
  overflow: hidden;
`;

const Bar = styled.div`
  height: 100%;
  background: ${props => props.theme.primary};
  width: ${props => props.percentage}%;
  transition: width 0.3s ease;
`;

const BarValue = styled.span`
  font-size: 12px;
  color: ${props => props.theme.metaText};
  min-width: 40px;
  text-align: right;
`;

const ClipboardStats = () => {
  const {
    history,
    getHistoryByType,
    getActiveContexts
  } = useClipboardManagerStore();

  const totalItems = history.length;
  const activeContexts = getActiveContexts().length;
  const types = ['text', 'code', 'url', 'filepath'];
  
  const typeCounts = types.reduce((acc, type) => {
    acc[type] = getHistoryByType(type).length;
    return acc;
  }, {});

  const getTypePercentage = (type) => {
    return totalItems > 0 ? Math.round((typeCounts[type] / totalItems) * 100) : 0;
  };

  const getMostUsedType = () => {
    return Object.entries(typeCounts).reduce((a, b) => 
      a[1] > b[1] ? a : b
    )[0];
  };

  return (
    <StatsContainer>
      <StatCard>
        <StatTitle>Total Items</StatTitle>
        <StatValue>{totalItems}</StatValue>
        <StatSubtext>In clipboard history</StatSubtext>
      </StatCard>

      <StatCard>
        <StatTitle>Active Contexts</StatTitle>
        <StatValue>{activeContexts}</StatValue>
        <StatSubtext>Currently active</StatSubtext>
      </StatCard>

      <StatCard>
        <StatTitle>Most Used Type</StatTitle>
        <StatValue>{getMostUsedType()}</StatValue>
        <StatSubtext>Based on usage</StatSubtext>
      </StatCard>

      <StatCard>
        <StatTitle>Type Distribution</StatTitle>
        <TypeDistribution>
          {types.map(type => (
            <TypeBar key={type}>
              <TypeLabel>{type}</TypeLabel>
              <BarContainer>
                <Bar percentage={getTypePercentage(type)} />
              </BarContainer>
              <BarValue>{typeCounts[type]}</BarValue>
            </TypeBar>
          ))}
        </TypeDistribution>
      </StatCard>
    </StatsContainer>
  );
};

export default ClipboardStats; 