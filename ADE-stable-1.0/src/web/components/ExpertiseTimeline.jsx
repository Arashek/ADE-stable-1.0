import React from 'react';
import {
  Box,
  Paper,
  Typography,
  Grid,
  LinearProgress,
  Tooltip,
  IconButton
} from '@mui/material';
import {
  TrendingUp as TrendingUpIcon,
  Info as InfoIcon
} from '@mui/icons-material';
import { Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip as ChartTooltip,
  Legend
} from 'chart.js';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  ChartTooltip,
  Legend
);

const ExpertiseTimeline = ({ expertiseData, learningHistory }) => {
  // Process data for timeline
  const timelineData = {
    labels: learningHistory.map(event => new Date(event.timestamp).toLocaleDateString()),
    datasets: Object.keys(expertiseData).map(domain => ({
      label: domain,
      data: learningHistory
        .filter(event => event.topic.toLowerCase().includes(domain.toLowerCase()))
        .map((_, index) => expertiseData[domain] * (index + 1) / learningHistory.length),
      borderColor: `hsl(${Math.random() * 360}, 70%, 50%)`,
      tension: 0.4
    }))
  };

  const options = {
    responsive: true,
    plugins: {
      legend: {
        position: 'top',
      },
      title: {
        display: true,
        text: 'Expertise Growth Timeline'
      }
    },
    scales: {
      y: {
        beginAtZero: true,
        max: 1
      }
    }
  };

  return (
    <Paper sx={{ p: 2 }}>
      <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
        <Typography variant="h6">
          Expertise Development
        </Typography>
        <Tooltip title="Shows how your expertise has grown over time based on learning events">
          <IconButton size="small">
            <InfoIcon />
          </IconButton>
        </Tooltip>
      </Box>

      <Grid container spacing={2}>
        <Grid item xs={12} md={8}>
          <Line data={timelineData} options={options} />
        </Grid>
        <Grid item xs={12} md={4}>
          <Box sx={{ mt: 2 }}>
            <Typography variant="subtitle1" gutterBottom>
              Current Expertise Levels
            </Typography>
            {Object.entries(expertiseData).map(([domain, level]) => (
              <Box key={domain} sx={{ mb: 1 }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
                  <Typography variant="body2">{domain}</Typography>
                  <Typography variant="body2" color="textSecondary">
                    {(level * 100).toFixed(1)}%
                  </Typography>
                </Box>
                <LinearProgress
                  variant="determinate"
                  value={level * 100}
                  sx={{
                    height: 8,
                    borderRadius: 4,
                    backgroundColor: 'rgba(0,0,0,0.1)',
                    '& .MuiLinearProgress-bar': {
                      borderRadius: 4
                    }
                  }}
                />
              </Box>
            ))}
          </Box>
        </Grid>
      </Grid>
    </Paper>
  );
};

export default ExpertiseTimeline; 