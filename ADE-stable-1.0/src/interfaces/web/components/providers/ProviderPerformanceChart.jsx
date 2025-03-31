import React from 'react';
import styled from 'styled-components';
import { FaChartBar, FaClock, FaExclamationTriangle } from 'react-icons/fa';
import PropTypes from 'prop-types';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';

const ChartContainer = styled.div`
  background: white;
  border-radius: 8px;
  padding: 24px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
`;

const ChartHeader = styled.div`
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

const MetricSelector = styled.div`
  display: flex;
  gap: 8px;
`;

const MetricButton = styled.button`
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

const ChartWrapper = styled.div`
  height: 400px;
  width: 100%;
`;

const LegendContainer = styled.div`
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
  margin-top: 16px;
`;

const LegendItem = styled.div`
  display: flex;
  align-items: center;
  gap: 8px;
`;

const ColorDot = styled.div`
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background: ${props => props.color};
`;

const LegendLabel = styled.span`
  font-size: 14px;
  color: #64748b;
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

const ProviderPerformanceChart = ({ providers, timeRange, metric, onMetricChange }) => {
  const formatDuration = (ms) => {
    const seconds = Math.floor(ms / 1000);
    if (seconds < 60) return `${seconds}s`;
    const minutes = Math.floor(seconds / 60);
    if (minutes < 60) return `${minutes}m`;
    const hours = Math.floor(minutes / 60);
    return `${hours}h`;
  };

  const formatNumber = (num) => {
    return new Intl.NumberFormat().format(num);
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
    }).format(amount);
  };

  const getMetricValue = (provider, dataPoint) => {
    switch (metric) {
      case 'responseTime':
        return dataPoint.responseTime;
      case 'cost':
        return dataPoint.cost;
      case 'requests':
        return dataPoint.requests;
      default:
        return 0;
    }
  };

  const formatMetricValue = (value) => {
    switch (metric) {
      case 'responseTime':
        return formatDuration(value);
      case 'cost':
        return formatCurrency(value);
      case 'requests':
        return formatNumber(value);
      default:
        return value;
    }
  };

  const getMetricLabel = () => {
    switch (metric) {
      case 'responseTime':
        return 'Response Time';
      case 'cost':
        return 'Cost';
      case 'requests':
        return 'Requests';
      default:
        return '';
    }
  };

  const getMetricUnit = () => {
    switch (metric) {
      case 'responseTime':
        return 'ms';
      case 'cost':
        return 'USD';
      case 'requests':
        return 'count';
      default:
        return '';
    }
  };

  const colors = ['#3b82f6', '#10b981', '#6366f1', '#f59e0b', '#ef4444'];

  return (
    <ChartContainer>
      <ChartHeader>
        <Title>
          <FaChartBar />
          Performance Comparison
        </Title>
        <MetricSelector>
          <MetricButton
            active={metric === 'responseTime'}
            onClick={() => onMetricChange('responseTime')}
          >
            Response Time
          </MetricButton>
          <MetricButton
            active={metric === 'cost'}
            onClick={() => onMetricChange('cost')}
          >
            Cost
          </MetricButton>
          <MetricButton
            active={metric === 'requests'}
            onClick={() => onMetricChange('requests')}
          >
            Requests
          </MetricButton>
        </MetricSelector>
      </ChartHeader>

      <ChartWrapper>
        <ResponsiveContainer width="100%" height="100%">
          <LineChart
            data={providers[0]?.performanceData || []}
            margin={{
              top: 5,
              right: 30,
              left: 20,
              bottom: 5,
            }}
          >
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="timestamp" />
            <YAxis
              tickFormatter={formatMetricValue}
              label={{ value: getMetricLabel(), angle: -90, position: 'insideLeft' }}
            />
            <Tooltip
              formatter={formatMetricValue}
              labelFormatter={(label) => new Date(label).toLocaleString()}
            />
            <Legend />
            {providers.map((provider, index) => (
              <Line
                key={provider.id}
                type="monotone"
                dataKey={(dataPoint) => getMetricValue(provider, dataPoint)}
                name={provider.name}
                stroke={colors[index % colors.length]}
                strokeWidth={2}
                dot={false}
              />
            ))}
          </LineChart>
        </ResponsiveContainer>
      </ChartWrapper>

      <LegendContainer>
        {providers.map((provider, index) => (
          <LegendItem key={provider.id}>
            <ColorDot color={colors[index % colors.length]} />
            <LegendLabel>{provider.name}</LegendLabel>
          </LegendItem>
        ))}
      </LegendContainer>

      {providers.some(provider => provider.hasIssues) && (
        <WarningMessage>
          <FaExclamationTriangle />
          Some providers are experiencing performance issues. Check the details for more information.
        </WarningMessage>
      )}
    </ChartContainer>
  );
};

ProviderPerformanceChart.propTypes = {
  providers: PropTypes.arrayOf(
    PropTypes.shape({
      id: PropTypes.string.isRequired,
      name: PropTypes.string.isRequired,
      performanceData: PropTypes.arrayOf(
        PropTypes.shape({
          timestamp: PropTypes.number.isRequired,
          responseTime: PropTypes.number.isRequired,
          cost: PropTypes.number.isRequired,
          requests: PropTypes.number.isRequired,
        })
      ).isRequired,
      hasIssues: PropTypes.bool,
    })
  ).isRequired,
  timeRange: PropTypes.oneOf(['day', 'week', 'month']).isRequired,
  metric: PropTypes.oneOf(['responseTime', 'cost', 'requests']).isRequired,
  onMetricChange: PropTypes.func.isRequired,
};

export default ProviderPerformanceChart; 