import express from 'express';
import { Container } from '../../core/models/project/Container';
import { DevelopmentWorkflowManager } from '../../core/models/project/DevelopmentWorkflowManager';
import { Logger } from '../../core/logging/Logger';
import { authenticateToken } from '../middleware/auth';

const router = express.Router();
const logger = new Logger();

// Apply authentication middleware to all routes
router.use(authenticateToken);

// Get workflow configuration
router.get('/:containerId/config', async (req, res) => {
  try {
    const container = await Container.getById(req.params.containerId);
    if (!container) {
      return res.status(404).json({ error: 'Container not found' });
    }

    const workflowManager = new DevelopmentWorkflowManager(
      container,
      {} as any,
      logger
    );

    const config = workflowManager.getConfiguration();
    res.json(config);
  } catch (error) {
    logger.error('Error getting workflow configuration:', error);
    res.status(500).json({ error: 'Failed to get workflow configuration' });
  }
});

// Update workflow configuration
router.put('/:containerId/config', async (req, res) => {
  try {
    const container = await Container.getById(req.params.containerId);
    if (!container) {
      return res.status(404).json({ error: 'Container not found' });
    }

    const workflowManager = new DevelopmentWorkflowManager(
      container,
      {} as any,
      logger
    );

    await workflowManager.updateConfiguration(req.body);
    res.json({ message: 'Configuration updated successfully' });
  } catch (error) {
    logger.error('Error updating workflow configuration:', error);
    res.status(500).json({ error: 'Failed to update workflow configuration' });
  }
});

// Get workflow status
router.get('/:containerId/status', async (req, res) => {
  try {
    const container = await Container.getById(req.params.containerId);
    if (!container) {
      return res.status(404).json({ error: 'Container not found' });
    }

    const workflowManager = new DevelopmentWorkflowManager(
      container,
      {} as any,
      logger
    );

    const status = workflowManager.getStatus();
    res.json(status);
  } catch (error) {
    logger.error('Error getting workflow status:', error);
    res.status(500).json({ error: 'Failed to get workflow status' });
  }
});

// Get workflow result
router.get('/:containerId/result', async (req, res) => {
  try {
    const container = await Container.getById(req.params.containerId);
    if (!container) {
      return res.status(404).json({ error: 'Container not found' });
    }

    const workflowManager = new DevelopmentWorkflowManager(
      container,
      {} as any,
      logger
    );

    const result = workflowManager.getResult();
    res.json(result);
  } catch (error) {
    logger.error('Error getting workflow result:', error);
    res.status(500).json({ error: 'Failed to get workflow result' });
  }
});

// Start workflow
router.post('/:containerId/start', async (req, res) => {
  try {
    const container = await Container.getById(req.params.containerId);
    if (!container) {
      return res.status(404).json({ error: 'Container not found' });
    }

    const workflowManager = new DevelopmentWorkflowManager(
      container,
      {} as any,
      logger
    );

    await workflowManager.startWorkflow();
    res.json({ message: 'Workflow started successfully' });
  } catch (error) {
    logger.error('Error starting workflow:', error);
    res.status(500).json({ error: 'Failed to start workflow' });
  }
});

// Stop workflow
router.post('/:containerId/stop', async (req, res) => {
  try {
    const container = await Container.getById(req.params.containerId);
    if (!container) {
      return res.status(404).json({ error: 'Container not found' });
    }

    const workflowManager = new DevelopmentWorkflowManager(
      container,
      {} as any,
      logger
    );

    await workflowManager.stopWorkflow();
    res.json({ message: 'Workflow stopped successfully' });
  } catch (error) {
    logger.error('Error stopping workflow:', error);
    res.status(500).json({ error: 'Failed to stop workflow' });
  }
});

export default router; 