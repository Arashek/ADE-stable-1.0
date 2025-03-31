import express from 'express';
import performanceRoutes from './performance';

const router = express.Router();

// ... existing routes ...

// Performance monitoring routes
router.use('/performance', performanceRoutes);

export default router; 