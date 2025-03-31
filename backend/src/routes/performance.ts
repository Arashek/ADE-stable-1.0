import express from 'express';
import { PerformanceMetrics } from '../types/performance';
import { calculateModelMetrics } from '../services/modelMetrics';
import { calculateAgentMetrics } from '../services/agentMetrics';
import { calculateSystemMetrics } from '../services/systemMetrics';
import { calculateQualityMetrics } from '../services/qualityMetrics';
import { getHistoricalData } from '../services/historicalData';

const router = express.Router();

router.get('/metrics', async (req, res) => {
  try {
    const { projectId, timeRange } = req.query;

    if (!projectId || !timeRange) {
      return res.status(400).json({ error: 'Missing required parameters' });
    }

    // Calculate current metrics
    const modelMetrics = await calculateModelMetrics(projectId as string);
    const agentMetrics = await calculateAgentMetrics(projectId as string);
    const systemMetrics = await calculateSystemMetrics(projectId as string);
    const qualityMetrics = await calculateQualityMetrics(projectId as string);

    // Get historical data
    const historicalData = await getHistoricalData(
      projectId as string,
      timeRange as string
    );

    const metrics: PerformanceMetrics = {
      model: {
        ...modelMetrics,
        historicalData: historicalData.model,
      },
      agent: {
        ...agentMetrics,
        historicalData: historicalData.agent,
      },
      system: {
        ...systemMetrics,
        historicalData: historicalData.system,
      },
      quality: {
        ...qualityMetrics,
        historicalData: historicalData.quality,
      },
    };

    res.json(metrics);
  } catch (error) {
    console.error('Error fetching performance metrics:', error);
    res.status(500).json({ error: 'Failed to fetch performance metrics' });
  }
});

export default router; 