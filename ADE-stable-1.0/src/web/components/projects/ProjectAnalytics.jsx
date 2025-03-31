import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { FaChartLine, FaChartBar, FaChartPie, FaUsers, FaClock, FaCheck, FaExclamationTriangle } from 'react-icons/fa';
import axios from 'axios';
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  PieChart,
  Pie,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer
} from 'recharts';

const Container = styled.div`
  padding: 20px;
  background: #f5f5f5;
  min-height: 100vh;
`;

const Header = styled.div`
  background: white;
  padding: 20px;
  border-radius: 8px;
  margin-bottom: 20px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
`;

const Title = styled.h1`
  margin: 0;
  color: #333;
  display: flex;
  align-items: center;
  gap: 10px;
`;

const MetricsGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
`;

const MetricCard = styled.div`
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
`;

const MetricTitle = styled.h3`
  margin: 0 0 10px 0;
  color: #666;
  font-size: 14px;
  display: flex;
  align-items: center;
  gap: 8px;
`;

const MetricValue = styled.div`
  font-size: 24px;
  font-weight: bold;
  color: #333;
`;

const MetricTrend = styled.div`
  font-size: 14px;
  color: ${props => props.positive ? '#28a745' : '#dc3545'};
  margin-top: 5px;
`;

const ChartContainer = styled.div`
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  margin-bottom: 20px;
  height: 400px;
`;

const ChartTitle = styled.h2`
  margin: 0 0 20px 0;
  color: #333;
  font-size: 18px;
`;

const TimeRangeSelector = styled.div`
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
`;

const TimeRangeButton = styled.button`
  padding: 8px 16px;
  border-radius: 4px;
  font-size: 14px;
  cursor: pointer;
  background: ${props => props.active ? '#007bff' : 'none'};
  color: ${props => props.active ? 'white' : '#666'};
  border: 1px solid ${props => props.active ? '#007bff' : '#ddd'};
  
  &:hover {
    background: ${props => props.active ? '#0056b3' : '#f5f5f5'};
  }
`;

const ProjectAnalytics = ({ projectId }) => {
  const [timeRange, setTimeRange] = useState('week');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [metrics, setMetrics] = useState({
    totalTasks: 0,
    completedTasks: 0,
    completionRate: 0,
    averageTimeToComplete: 0,
    activeContributors: 0,
    taskTrend: [],
    statusDistribution: [],
    contributorActivity: []
  });
  
  useEffect(() => {
    fetchAnalytics();
  }, [projectId, timeRange]);
  
  const fetchAnalytics = async () => {
    try {
      const response = await axios.get(`/api/projects/${projectId}/analytics`, {
        params: { timeRange }
      });
      setMetrics(response.data);
    } catch (err) {
      setError('Failed to fetch analytics data');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };
  
  if (loading) {
    return <div>Loading...</div>;
  }
  
  return (
    <Container>
      <Header>
        <Title>
          <FaChartLine />
          Project Analytics
        </Title>
      </Header>
      
      {error && (
        <div style={{ color: 'red', marginBottom: '20px' }}>
          {error}
        </div>
      )}
      
      <TimeRangeSelector>
        <TimeRangeButton
          active={timeRange === 'week'}
          onClick={() => setTimeRange('week')}
        >
          Week
        </TimeRangeButton>
        <TimeRangeButton
          active={timeRange === 'month'}
          onClick={() => setTimeRange('month')}
        >
          Month
        </TimeRangeButton>
        <TimeRangeButton
          active={timeRange === 'quarter'}
          onClick={() => setTimeRange('quarter')}
        >
          Quarter
        </TimeRangeButton>
      </TimeRangeSelector>
      
      <MetricsGrid>
        <MetricCard>
          <MetricTitle>
            <FaCheck />
            Completion Rate
          </MetricTitle>
          <MetricValue>{metrics.completionRate}%</MetricValue>
          <MetricTrend positive={metrics.completionRate >= 80}>
            {metrics.completionRate >= 80 ? 'On Track' : 'Needs Attention'}
          </MetricTrend>
        </MetricCard>
        
        <MetricCard>
          <MetricTitle>
            <FaClock />
            Avg. Time to Complete
          </MetricTitle>
          <MetricValue>{metrics.averageTimeToComplete} days</MetricValue>
          <MetricTrend positive={metrics.averageTimeToComplete <= 7}>
            {metrics.averageTimeToComplete <= 7 ? 'Efficient' : 'Needs Improvement'}
          </MetricTrend>
        </MetricCard>
        
        <MetricCard>
          <MetricTitle>
            <FaUsers />
            Active Contributors
          </MetricTitle>
          <MetricValue>{metrics.activeContributors}</MetricValue>
          <MetricTrend positive={metrics.activeContributors >= 3}>
            {metrics.activeContributors >= 3 ? 'Good Team Size' : 'Consider Adding Members'}
          </MetricTrend>
        </MetricCard>
        
        <MetricCard>
          <MetricTitle>
            <FaExclamationTriangle />
            Tasks Status
          </MetricTitle>
          <MetricValue>
            {metrics.completedTasks}/{metrics.totalTasks}
          </MetricValue>
          <MetricTrend positive={metrics.completedTasks / metrics.totalTasks >= 0.8}>
            {metrics.completedTasks / metrics.totalTasks >= 0.8 ? 'On Schedule' : 'Behind Schedule'}
          </MetricTrend>
        </MetricCard>
      </MetricsGrid>
      
      <ChartContainer>
        <ChartTitle>Task Completion Trend</ChartTitle>
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={metrics.taskTrend}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="date" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Line
              type="monotone"
              dataKey="completed"
              stroke="#28a745"
              name="Completed Tasks"
            />
            <Line
              type="monotone"
              dataKey="total"
              stroke="#007bff"
              name="Total Tasks"
            />
          </LineChart>
        </ResponsiveContainer>
      </ChartContainer>
      
      <ChartContainer>
        <ChartTitle>Task Status Distribution</ChartTitle>
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Pie
              data={metrics.statusDistribution}
              dataKey="value"
              nameKey="name"
              cx="50%"
              cy="50%"
              outerRadius={150}
              label
            />
            <Tooltip />
            <Legend />
          </PieChart>
        </ResponsiveContainer>
      </ChartContainer>
      
      <ChartContainer>
        <ChartTitle>Contributor Activity</ChartTitle>
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={metrics.contributorActivity}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="name" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Bar
              dataKey="tasks"
              fill="#007bff"
              name="Tasks Completed"
            />
            <Bar
              dataKey="commits"
              fill="#28a745"
              name="Commits"
            />
          </BarChart>
        </ResponsiveContainer>
      </ChartContainer>
    </Container>
  );
};

export default ProjectAnalytics; 