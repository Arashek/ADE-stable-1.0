import { ModelMetrics } from '../types/performance';
import { db } from '../db';

export async function calculateModelMetrics(projectId: string): Promise<ModelMetrics> {
  try {
    // Get recent model interactions
    const recentInteractions = await db.modelInteractions.findMany({
      where: {
        projectId,
        timestamp: {
          gte: new Date(Date.now() - 24 * 60 * 60 * 1000), // Last 24 hours
        },
      },
      orderBy: {
        timestamp: 'desc',
      },
    });

    // Calculate response time metrics
    const responseTimes = recentInteractions.map(interaction => 
      interaction.endTime.getTime() - interaction.startTime.getTime()
    );
    const avgResponseTime = responseTimes.reduce((a, b) => a + b, 0) / responseTimes.length;

    // Calculate success and error rates
    const totalRequests = recentInteractions.length;
    const successfulRequests = recentInteractions.filter(i => i.status === 'success').length;
    const errorRequests = recentInteractions.filter(i => i.status === 'error').length;
    
    const successRate = (successfulRequests / totalRequests) * 100;
    const errorRate = (errorRequests / totalRequests) * 100;

    // Calculate token usage and cost
    const totalTokens = recentInteractions.reduce((sum, i) => sum + i.tokenUsage, 0);
    const costPerRequest = recentInteractions.reduce((sum, i) => sum + i.cost, 0) / totalRequests;

    return {
      responseTime: avgResponseTime,
      successRate,
      errorRate,
      tokenUsage: totalTokens,
      costPerRequest,
      historicalData: [], // Will be populated by historicalData service
    };
  } catch (error) {
    console.error('Error calculating model metrics:', error);
    throw error;
  }
} 