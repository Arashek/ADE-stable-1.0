import express from 'express';
import { metricsService } from '../services/metricsService';
import { rateLimiterService } from '../services/rateLimiterService';
import { websocketServer } from '../websocket/websocketServer';

const router = express.Router();

router.get('/metrics', async (req, res) => {
  try {
    const metrics = await metricsService.getMetrics();
    res.json(metrics);
  } catch (error) {
    console.error('Error fetching metrics:', error);
    res.status(500).json({ error: 'Failed to fetch metrics' });
  }
});

router.get('/metrics/histogram/:metric', async (req, res) => {
  try {
    const { metric } = req.params;
    const histogram = await metricsService.getHistogram(metric);
    res.json(histogram);
  } catch (error) {
    console.error('Error fetching histogram:', error);
    res.status(500).json({ error: 'Failed to fetch histogram' });
  }
});

router.get('/metrics/server', async (req, res) => {
  try {
    const serverMetrics = await websocketServer.getServerMetrics();
    res.json(serverMetrics);
  } catch (error) {
    console.error('Error fetching server metrics:', error);
    res.status(500).json({ error: 'Failed to fetch server metrics' });
  }
});

router.get('/metrics/rate-limits', async (req, res) => {
  try {
    const rateLimits = await rateLimiterService.getRateLimitMetrics();
    res.json(rateLimits);
  } catch (error) {
    console.error('Error fetching rate limit metrics:', error);
    res.status(500).json({ error: 'Failed to fetch rate limit metrics' });
  }
});

export default router; 