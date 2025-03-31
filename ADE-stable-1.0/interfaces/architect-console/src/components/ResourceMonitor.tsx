import React from 'react';
import { Paper, Typography, Grid, Box } from '@mui/material';
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

// Sample data for demonstration
const data = [
  { time: '00:00', cpu: 65, memory: 45, disk: 30 },
  { time: '01:00', cpu: 70, memory: 50, disk: 35 },
  { time: '02:00', cpu: 75, memory: 55, disk: 40 },
  { time: '03:00', cpu: 80, memory: 60, disk: 45 },
  { time: '04:00', cpu: 85, memory: 65, disk: 50 },
  { time: '05:00', cpu: 90, memory: 70, disk: 55 },
  { time: '06:00', cpu: 85, memory: 65, disk: 50 },
  { time: '07:00', cpu: 80, memory: 60, disk: 45 },
  { time: '08:00', cpu: 75, memory: 55, disk: 40 },
  { time: '09:00', cpu: 70, memory: 50, disk: 35 },
  { time: '10:00', cpu: 65, memory: 45, disk: 30 },
];

const ResourceMonitor: React.FC = () => {
  return (
    <Paper elevation={3} sx={{ p: 2 }}>
      <Typography variant="h6" gutterBottom>
        Resource Monitor
      </Typography>
      <Grid container spacing={2}>
        <Grid item xs={12}>
          <Box sx={{ height: 300 }}>
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={data}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="time" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Line
                  type="monotone"
                  dataKey="cpu"
                  stroke="#8884d8"
                  name="CPU Usage (%)"
                />
                <Line
                  type="monotone"
                  dataKey="memory"
                  stroke="#82ca9d"
                  name="Memory Usage (%)"
                />
                <Line
                  type="monotone"
                  dataKey="disk"
                  stroke="#ffc658"
                  name="Disk Usage (%)"
                />
              </LineChart>
            </ResponsiveContainer>
          </Box>
        </Grid>
      </Grid>
    </Paper>
  );
};

export default ResourceMonitor; 