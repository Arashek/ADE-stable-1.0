import { Router } from 'express';
import { container } from 'tsyringe';
import { AgentService } from '../services/agent/AgentService';
import { AgentRegistry } from '../services/agent/AgentRegistry';
import { LLMProviderService } from '../services/agent/LLMProviderService';
import { validateAgentConfig, validateLLMEndpoint } from '../validators/agentValidators';
import { authenticateUser, authorizeRole, validateApiKey } from '../middleware/auth';
import { rateLimiter } from '../middleware/rateLimiter';
import { z } from 'zod';
import { AdvancedAgentCapabilities } from '../services/agent/AdvancedAgentCapabilities';

const router = Router();
const agentService = container.resolve(AgentService);
const agentRegistry = container.resolve(AgentRegistry);
const llmProviderService = container.resolve(LLMProviderService);

// Validation schemas
const agentConfigSchema = z.object({
  id: z.string().min(1),
  name: z.string().min(1),
  description: z.string(),
  capabilities: z.array(z.object({
    id: z.string(),
    name: z.string(),
    description: z.string(),
    requiredLLMs: z.array(z.string()),
    supportedActions: z.array(z.string()),
    parameters: z.record(z.any())
  })),
  defaultLLM: z.string(),
  fallbackLLMs: z.array(z.string()),
  isActive: z.boolean(),
  parameters: z.record(z.any()).optional()
});

const collaborationRequestSchema = z.object({
  sourceAgentId: z.string(),
  targetAgentId: z.string(),
  action: z.enum(['start', 'end']),
  context: z.record(z.any()).optional()
});

// Get all agents
router.get('/agents', authenticateUser, async (req, res) => {
  try {
    const inventory = agentService.getAgentInventory();
    res.json(Object.values(inventory.agents));
  } catch (error) {
    res.status(500).json({ error: 'Failed to fetch agents' });
  }
});

// Get agent registrations
router.get('/agents/registrations', authenticateUser, async (req, res) => {
  try {
    const registrations = agentRegistry.getAllRegistrations();
    res.json(registrations);
  } catch (error) {
    res.status(500).json({ error: 'Failed to fetch agent registrations' });
  }
});

// Register a new agent
router.post('/register',
  authenticateUser,
  authorizeRole(['admin', 'developer']),
  rateLimiter(50, 900), // 50 requests per 15 minutes
  async (req, res) => {
    try {
      const config = agentConfigSchema.parse(req.body);
      await agentRegistry.registerAgent(config);
      res.status(201).json({
        success: true,
        message: `Agent ${config.id} registered successfully`,
        data: config
      });
    } catch (error) {
      if (error instanceof z.ZodError) {
        res.status(400).json({
          success: false,
          message: 'Invalid agent configuration',
          errors: error.errors
        });
      } else {
        res.status(500).json({
          success: false,
          message: 'Failed to register agent',
          error: error instanceof Error ? error.message : 'Unknown error'
        });
      }
    }
  }
);

// Unregister an agent
router.delete('/:agentId',
  authenticateUser,
  authorizeRole(['admin', 'developer']),
  rateLimiter(50, 900),
  async (req, res) => {
    try {
      const { agentId } = req.params;
      await agentRegistry.unregisterAgent(agentId);
      res.json({
        success: true,
        message: `Agent ${agentId} unregistered successfully`
      });
    } catch (error) {
      res.status(500).json({
        success: false,
        message: 'Failed to unregister agent',
        error: error instanceof Error ? error.message : 'Unknown error'
      });
    }
  }
);

// Get agent inventory
router.get('/inventory',
  authenticateUser,
  authorizeRole(['admin', 'developer', 'viewer']),
  rateLimiter(100, 900),
  async (req, res) => {
    try {
      const inventory = agentService.getAgentInventory();
      res.json({
        success: true,
        data: inventory
      });
    } catch (error) {
      res.status(500).json({
        success: false,
        message: 'Failed to get agent inventory',
        error: error instanceof Error ? error.message : 'Unknown error'
      });
    }
  }
);

// Get agent by ID
router.get('/:agentId',
  authenticateUser,
  authorizeRole(['admin', 'developer', 'viewer']),
  rateLimiter(100, 900),
  async (req, res) => {
    try {
      const { agentId } = req.params;
      const agent = agentService.getAgent(agentId);
      if (!agent) {
        res.status(404).json({
          success: false,
          message: `Agent ${agentId} not found`
        });
        return;
      }
      res.json({
        success: true,
        data: agent
      });
    } catch (error) {
      res.status(500).json({
        success: false,
        message: 'Failed to get agent',
        error: error instanceof Error ? error.message : 'Unknown error'
      });
    }
  }
);

// Update agent status
router.patch('/:agentId/status',
  authenticateUser,
  authorizeRole(['admin', 'developer']),
  rateLimiter(50, 900),
  async (req, res) => {
    try {
      const { agentId } = req.params;
      const { status, error } = req.body;
      
      if (!['active', 'inactive', 'error'].includes(status)) {
        res.status(400).json({
          success: false,
          message: 'Invalid status value'
        });
        return;
      }

      await agentRegistry.updateAgentStatus(agentId, status, error);
      res.json({
        success: true,
        message: `Agent ${agentId} status updated to ${status}`
      });
    } catch (error) {
      res.status(500).json({
        success: false,
        message: 'Failed to update agent status',
        error: error instanceof Error ? error.message : 'Unknown error'
      });
    }
  }
);

// Get all LLM endpoints
router.get('/llm/endpoints', authenticateUser, async (req, res) => {
  try {
    const endpoints = llmProviderService.getActiveEndpoints();
    res.json(endpoints);
  } catch (error) {
    res.status(500).json({ error: 'Failed to fetch LLM endpoints' });
  }
});

// Get all LLM providers
router.get('/llm/providers', authenticateUser, async (req, res) => {
  try {
    const providers = llmProviderService.getAllProviders();
    res.json(providers);
  } catch (error) {
    res.status(500).json({ error: 'Failed to fetch LLM providers' });
  }
});

// Register new LLM endpoint
router.post('/llm/endpoints', authenticateUser, rateLimiter(50, 15 * 60), async (req, res) => {
  try {
    const endpoint = req.body;
    
    // Validate endpoint configuration
    const validationError = validateLLMEndpoint(endpoint);
    if (validationError) {
      return res.status(400).json({ error: validationError });
    }

    // Validate endpoint with provider service
    const isValid = await llmProviderService.validateEndpoint(endpoint);
    if (!isValid) {
      return res.status(400).json({ error: 'Invalid endpoint configuration' });
    }

    // Register endpoint
    await llmProviderService.registerEndpoint(endpoint);
    res.status(201).json(endpoint);
  } catch (error) {
    res.status(500).json({ error: 'Failed to register LLM endpoint' });
  }
});

// Update LLM endpoint status
router.patch('/llm/endpoints/:endpointId/status', authenticateUser, async (req, res) => {
  try {
    const { endpointId } = req.params;
    const { isActive } = req.body;

    await llmProviderService.updateEndpointStatus(endpointId, isActive);
    res.json({ message: 'Endpoint status updated successfully' });
  } catch (error) {
    res.status(500).json({ error: 'Failed to update endpoint status' });
  }
});

// Unregister LLM endpoint
router.delete('/llm/endpoints/:endpointId', authenticateUser, async (req, res) => {
  try {
    const { endpointId } = req.params;
    await llmProviderService.unregisterEndpoint(endpointId);
    res.json({ message: 'Endpoint unregistered successfully' });
  } catch (error) {
    res.status(500).json({ error: 'Failed to unregister endpoint' });
  }
});

// Get agent capabilities
router.get('/agents/:agentId/capabilities', authenticateUser, async (req, res) => {
  try {
    const { agentId } = req.params;
    const agent = agentService.getAgent(agentId);
    
    if (!agent) {
      return res.status(404).json({ error: 'Agent not found' });
    }

    res.json(agent.capabilities);
  } catch (error) {
    res.status(500).json({ error: 'Failed to fetch agent capabilities' });
  }
});

// Find agents by capability
router.get('/agents/by-capability/:capability', authenticateUser, async (req, res) => {
  try {
    const { capability } = req.params;
    const agents = await agentRegistry.findAgentsByCapability(capability);
    res.json(agents);
  } catch (error) {
    res.status(500).json({ error: 'Failed to find agents by capability' });
  }
});

// Verify agent capabilities
router.get('/:agentId/capabilities/verify',
  authenticateUser,
  authorizeRole(['admin', 'developer']),
  rateLimiter(50, 900),
  async (req, res) => {
    try {
      const { agentId } = req.params;
      const result = await agentService.verifyAgentCapabilities(agentId);
      res.json({
        success: true,
        data: result
      });
    } catch (error) {
      res.status(500).json({
        success: false,
        message: 'Failed to verify agent capabilities',
        error: error instanceof Error ? error.message : 'Unknown error'
      });
    }
  }
);

// Get capability statistics
router.get('/capabilities/stats',
  authenticateUser,
  authorizeRole(['admin', 'developer', 'viewer']),
  rateLimiter(100, 900),
  async (req, res) => {
    try {
      const stats = agentService.getCapabilityStats();
      res.json({
        success: true,
        data: stats
      });
    } catch (error) {
      res.status(500).json({
        success: false,
        message: 'Failed to get capability statistics',
        error: error instanceof Error ? error.message : 'Unknown error'
      });
    }
  }
);

// Update LLM mapping
router.put('/llm/:llmId/mapping',
  authenticateUser,
  authorizeRole(['admin']),
  rateLimiter(30, 900),
  async (req, res) => {
    try {
      const { llmId } = req.params;
      const { endpoints } = req.body;
      
      if (!Array.isArray(endpoints)) {
        res.status(400).json({
          success: false,
          message: 'Endpoints must be an array'
        });
        return;
      }

      await agentService.updateLLMMapping(llmId, endpoints);
      res.json({
        success: true,
        message: `LLM mapping updated for ${llmId}`
      });
    } catch (error) {
      res.status(500).json({
        success: false,
        message: 'Failed to update LLM mapping',
        error: error instanceof Error ? error.message : 'Unknown error'
      });
    }
  }
);

// WebSocket Preview Endpoints

// Get preview URL for agent
router.get('/:agentId/preview-url',
  authenticateUser,
  authorizeRole(['admin', 'developer', 'viewer']),
  rateLimiter(100, 900),
  async (req, res) => {
    try {
      const { agentId } = req.params;
      const registration = agentRegistry.getRegistration(agentId);
      
      if (!registration) {
        res.status(404).json({
          success: false,
          message: `Agent ${agentId} not found`
        });
        return;
      }

      res.json({
        success: true,
        data: {
          previewUrl: registration.previewUrl
        }
      });
    } catch (error) {
      res.status(500).json({
        success: false,
        message: 'Failed to get preview URL',
        error: error instanceof Error ? error.message : 'Unknown error'
      });
    }
  }
);

// Get advanced capabilities
router.get('/capabilities/advanced',
  authenticateUser,
  authorizeRole(['admin', 'developer', 'viewer']),
  rateLimiter(100, 900),
  async (req, res) => {
    try {
      const advancedCapabilities = container.resolve(AdvancedAgentCapabilities);
      const capabilities = advancedCapabilities.getCapabilities();
      res.json({
        success: true,
        data: capabilities
      });
    } catch (error) {
      res.status(500).json({
        success: false,
        message: 'Failed to get advanced capabilities',
        error: error instanceof Error ? error.message : 'Unknown error'
      });
    }
  }
);

// Get capabilities by LLM
router.get('/capabilities/llm/:llmId',
  authenticateUser,
  authorizeRole(['admin', 'developer', 'viewer']),
  rateLimiter(100, 900),
  async (req, res) => {
    try {
      const { llmId } = req.params;
      const advancedCapabilities = container.resolve(AdvancedAgentCapabilities);
      const capabilities = advancedCapabilities.getCapabilitiesByLLM(llmId);
      res.json({
        success: true,
        data: capabilities
      });
    } catch (error) {
      res.status(500).json({
        success: false,
        message: 'Failed to get capabilities by LLM',
        error: error instanceof Error ? error.message : 'Unknown error'
      });
    }
  }
);

// Get capabilities by action
router.get('/capabilities/action/:action',
  authenticateUser,
  authorizeRole(['admin', 'developer', 'viewer']),
  rateLimiter(100, 900),
  async (req, res) => {
    try {
      const { action } = req.params;
      const advancedCapabilities = container.resolve(AdvancedAgentCapabilities);
      const capabilities = advancedCapabilities.getCapabilitiesByAction(action);
      res.json({
        success: true,
        data: capabilities
      });
    } catch (error) {
      res.status(500).json({
        success: false,
        message: 'Failed to get capabilities by action',
        error: error instanceof Error ? error.message : 'Unknown error'
      });
    }
  }
);

// Get capability by ID
router.get('/capabilities/:capabilityId',
  authenticateUser,
  authorizeRole(['admin', 'developer', 'viewer']),
  rateLimiter(100, 900),
  async (req, res) => {
    try {
      const { capabilityId } = req.params;
      const advancedCapabilities = container.resolve(AdvancedAgentCapabilities);
      const capability = advancedCapabilities.getCapabilityById(capabilityId);
      
      if (!capability) {
        res.status(404).json({
          success: false,
          message: `Capability ${capabilityId} not found`
        });
        return;
      }

      res.json({
        success: true,
        data: capability
      });
    } catch (error) {
      res.status(500).json({
        success: false,
        message: 'Failed to get capability',
        error: error instanceof Error ? error.message : 'Unknown error'
      });
    }
  }
);

export default router;

 