import { Router } from 'express';
import { DesignAgent } from '../services/design/DesignAgent';
import { DesignRequest } from '../services/design/types';
import { validateDesignRequest } from '../middleware/validators';
import { authenticateUser } from '../middleware/auth';
import { rateLimit } from '../middleware/rateLimit';

const router = Router();
const designAgent = DesignAgent.getInstance();

// Rate limiting configuration for design endpoints
const designRateLimit = rateLimit({
    windowMs: 15 * 60 * 1000, // 15 minutes
    max: 50 // limit each IP to 50 requests per windowMs
});

// Generate UI mockup
router.post('/mockup', 
    authenticateUser,
    designRateLimit,
    validateDesignRequest,
    async (req, res) => {
        try {
            const request: DesignRequest = req.body;
            const response = await designAgent.generateUIMockup(request);
            res.json(response);
        } catch (error) {
            console.error('Error generating UI mockup:', error);
            res.status(500).json({ 
                error: 'Failed to generate UI mockup',
                details: error.message 
            });
        }
    }
);

// Analyze existing design
router.post('/analyze',
    authenticateUser,
    designRateLimit,
    async (req, res) => {
        try {
            const { design } = req.body;
            const feedback = await designAgent.analyzeExistingDesign(design);
            res.json(feedback);
        } catch (error) {
            console.error('Error analyzing design:', error);
            res.status(500).json({ 
                error: 'Failed to analyze design',
                details: error.message 
            });
        }
    }
);

// Generate visual assets
router.post('/assets',
    authenticateUser,
    designRateLimit,
    async (req, res) => {
        try {
            const request: DesignRequest = req.body;
            const assets = await designAgent.generateVisualAssets(request);
            res.json({ assets });
        } catch (error) {
            console.error('Error generating visual assets:', error);
            res.status(500).json({ 
                error: 'Failed to generate visual assets',
                details: error.message 
            });
        }
    }
);

// Get design cache stats
router.get('/cache/stats',
    authenticateUser,
    async (req, res) => {
        try {
            const cache = designAgent.getCache();
            const stats = cache.getCacheStats();
            res.json(stats);
        } catch (error) {
            console.error('Error getting cache stats:', error);
            res.status(500).json({ 
                error: 'Failed to get cache stats',
                details: error.message 
            });
        }
    }
);

// Clear design cache
router.post('/cache/clear',
    authenticateUser,
    async (req, res) => {
        try {
            const cache = designAgent.getCache();
            cache.clear();
            res.json({ message: 'Cache cleared successfully' });
        } catch (error) {
            console.error('Error clearing cache:', error);
            res.status(500).json({ 
                error: 'Failed to clear cache',
                details: error.message 
            });
        }
    }
);

export default router; 