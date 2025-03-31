import React from 'react';
import styled from 'styled-components';
import { FaChartLine, FaDollarSign, FaClock, FaExclamationTriangle } from 'react-icons/fa';
import PropTypes from 'prop-types';

const StatsContainer = styled.div`
  background: white;
  border-radius: 8px;
  padding: 24px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
`;

const StatsHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
`;

const Title = styled.h3`
  font-size: 18px;
  color: #1e293b;
  margin: 0;
  display: flex;
  align-items: center;
  gap: 8px;
`;

const TimeRange = styled.div`
  display: flex;
  gap: 8px;
`;

const TimeButton = styled.button`
  padding: 6px 12px;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  background: ${props => props.active ? '#3b82f6' : 'white'};
  color: ${props => props.active ? 'white' : '#64748b'};
  cursor: pointer;
  font-size: 14px;
  transition: all 0.2s;

  &:hover {
    background: ${props => props.active ? '#2563eb' : '#f8fafc'};
  }

  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
`;

const StatsGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 24px;
`;

const StatCard = styled.div`
  background: #f8fafc;
  border-radius: 8px;
  padding: 16px;
`;

const StatHeader = styled.div`
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
`;

const StatIcon = styled.div`
  width: 32px;
  height: 32px;
  border-radius: 8px;
  background: ${props => props.color};
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
`;

const StatTitle = styled.div`
  font-size: 14px;
  color: #64748b;
`;

const StatValue = styled.div`
  font-size: 24px;
  font-weight: 600;
  color: #1e293b;
`;

const StatSubtext = styled.div`
  font-size: 12px;
  color: #94a3b8;
  margin-top: 4px;
`;

const WarningMessage = styled.div`
  display: flex;
  align-items: center;
  gap: 8px;
  background: #fef3c7;
  color: #92400e;
  padding: 12px 16px;
  border-radius: 6px;
  margin-top: 16px;
`;

const ProviderUsageStats = ({ provider, timeRange, onTimeRangeChange }) => {
  const formatNumber = (num) => {
    return new Intl.NumberFormat().format(num);
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
    }).format(amount);
  };

  const formatDuration = (ms) => {
    const seconds = Math.floor(ms / 1000);
    if (seconds < 60) return `${seconds}s`;
    const minutes = Math.floor(seconds / 60);
    if (minutes < 60) return `${minutes}m`;
    const hours = Math.floor(minutes / 60);
    return `${hours}h`;
  };

  const getUsagePercentage = () => {
    if (!provider.quota) return 0;
    return (provider.usage / provider.quota) * 100;
  };

  const isNearQuota = () => {
    const percentage = getUsagePercentage();
    return percentage > 80;
  };

  return (
    <StatsContainer>
      <StatsHeader>
        <Title>
          <FaChartLine />
          Usage Statistics
        </Title>
        <TimeRange>
          <TimeButton
            active={timeRange === 'day'}
            onClick={() => onTimeRangeChange('day')}
          >
            Day
          </TimeButton>
          <TimeButton
            active={timeRange === 'week'}
            onClick={() => onTimeRangeChange('week')}
          >
            Week
          </TimeButton>
          <TimeButton
            active={timeRange === 'month'}
            onClick={() => onTimeRangeChange('month')}
          >
            Month
          </TimeButton>
        </TimeRange>
      </StatsHeader>

      <StatsGrid>
        <StatCard>
          <StatHeader>
            <StatIcon color="#3b82f6">
              <FaChartLine />
            </StatIcon>
            <StatTitle>Total Requests</StatTitle>
          </StatHeader>
          <StatValue>{formatNumber(provider.usage)}</StatValue>
          <StatSubtext>
            {formatNumber(provider.quota)} requests available
          </StatSubtext>
        </StatCard>

        <StatCard>
          <StatHeader>
            <StatIcon color="#10b981">
              <FaDollarSign />
            </StatIcon>
            <StatTitle>Cost</StatTitle>
          </StatHeader>
          <StatValue>{formatCurrency(provider.cost)}</StatValue>
          <StatSubtext>This {timeRange}</StatSubtext>
        </StatCard>

        <StatCard>
          <StatHeader>
            <StatIcon color="#6366f1">
              <FaClock />
            </StatIcon>
            <StatTitle>Avg. Response Time</StatTitle>
          </StatHeader>
          <StatValue>{formatDuration(provider.avgResponseTime)}</StatValue>
          <StatSubtext>Last 100 requests</StatSubtext>
        </StatCard>
      </StatsGrid>

      {isNearQuota() && (
        <WarningMessage>
          <FaExclamationTriangle />
          You are approaching your usage quota. Consider upgrading your plan.
        </WarningMessage>
      )}
    </StatsContainer>
  );
};

ProviderUsageStats.propTypes = {
  provider: PropTypes.shape({
    usage: PropTypes.number.isRequired,
    quota: PropTypes.number.isRequired,
    cost: PropTypes.number.isRequired,
    avgResponseTime: PropTypes.number.isRequired,
  }).isRequired,
  timeRange: PropTypes.oneOf(['day', 'week', 'month']).isRequired,
  onTimeRangeChange: PropTypes.func.isRequired,
};

 