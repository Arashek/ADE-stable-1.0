import React from 'react';
import {
  Box,
  Paper,
  Typography,
  Grid,
  Tooltip,
  IconButton,
  Card,
  CardContent,
  Divider
} from '@mui/material';
import {
  Info as InfoIcon,
  TrendingUp as TrendingUpIcon,
  Category as CategoryIcon,
  Timeline as TimelineIcon
} from '@mui/icons-material';
import {
  Chart as ChartJS,
  ArcElement,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip as ChartTooltip,
  Legend
} from 'chart.js';
import { Pie, Bar } from 'react-chartjs-2';

ChartJS.register(
  ArcElement,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  ChartTooltip,
  Legend
);

const KnowledgeAnalytics = ({ entries, stats, timeRange }) => {
  // Process data for visualizations
  const tagDistribution = entries.reduce((acc, entry) => {
    entry.tags.forEach(tag => {
      acc[tag] = (acc[tag] || 0) + 1;
    });
    return acc;
  }, {});

  const pieData = {
    labels: Object.keys(tagDistribution),
    datasets: [{
      data: Object.values(tagDistribution),
      backgroundColor: Object.keys(tagDistribution).map(() => 
        `hsl(${Math.random() * 360}, 70%, 50%)`
      )
    }]
  };

  const timeData = {
    labels: timeRange.map(date => new Date(date).toLocaleDateString()),
    datasets: [{
      label: 'Knowledge Growth',
      data: timeRange.map(date => 
        entries.filter(entry => 
          new Date(entry.created_at) <= new Date(date)
        ).length
      ),
      borderColor: 'rgb(75, 192, 192)',
      tension: 0.4
    }]
  };

  const barData = {
    labels: Object.keys(stats.expertise_by_domain),
    datasets: [{
      label: 'Expertise Distribution',
      data: Object.values(stats.expertise_by_domain),
      backgroundColor: 'rgba(75, 192, 192, 0.5)'
    }]
  };

  const options = {
    responsive: true,
    plugins: {
      legend: {
        position: 'top',
      },
      title: {
        display: true,
        text: 'Knowledge Analytics'
      }
    }
  };

  return (
    <Grid container spacing={2}>
      <Grid item xs={12}>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
          <Typography variant="h6">
            Knowledge Analytics
          </Typography>
          <Tooltip title="Comprehensive analytics of your knowledge base">
            <IconButton size="small">
              <InfoIcon />
            </IconButton>
          </Tooltip>
        </Box>
      </Grid>

      <Grid item xs={12} md={4}>
        <Card>
          <CardContent>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
              <CategoryIcon sx={{ mr: 1 }} />
              <Typography variant="subtitle1">Tag Distribution</Typography>
            </Box>
            <Pie data={pieData} options={options} />
          </CardContent>
        </Card>
      </Grid>

      <Grid item xs={12} md={4}>
        <Card>
          <CardContent>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
              <TimelineIcon sx={{ mr: 1 }} />
              <Typography variant="subtitle1">Knowledge Growth</Typography>
            </Box>
            <Bar data={timeData} options={options} />
          </CardContent>
        </Card>
      </Grid>

      <Grid item xs={12} md={4}>
        <Card>
          <CardContent>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
              <TrendingUpIcon sx={{ mr: 1 }} />
              <Typography variant="subtitle1">Expertise Distribution</Typography>
            </Box>
            <Bar data={barData} options={options} />
          </CardContent>
        </Card>
      </Grid>

      <Grid item xs={12}>
        <Divider sx={{ my: 2 }} />
      </Grid>

      <Grid item xs={12} md={3}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Total Entries
            </Typography>
            <Typography variant="h4">
              {stats.total_entries}
            </Typography>
          </CardContent>
        </Card>
      </Grid>

      <Grid item xs={12} md={3}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Active Agents
            </Typography>
            <Typography variant="h4">
              {stats.total_agents}
            </Typography>
          </CardContent>
        </Card>
      </Grid>

      <Grid item xs={12} md={3}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Total Tags
            </Typography>
            <Typography variant="h4">
              {Object.keys(tagDistribution).length}
            </Typography>
          </CardContent>
        </Card>
      </Grid>

      <Grid item xs={12} md={3}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Last Sync
            </Typography>
            <Typography variant="h4">
              {new Date(stats.last_sync).toLocaleDateString()}
            </Typography>
          </CardContent>
        </Card>
      </Grid>
    </Grid>
  );
};

export default KnowledgeAnalytics; 