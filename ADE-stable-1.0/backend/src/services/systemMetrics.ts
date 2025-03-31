import { SystemMetrics } from '../types/performance';
import { db } from '../db';

export async function calculateSystemMetrics(projectId: string): Promise<SystemMetrics> {
  try {
    // Get recent API calls
    const recentApiCalls = await db.apiCalls.findMany({
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

    // Calculate API latency
    const latencies = recentApiCalls.map(call => 
      call.endTime.getTime() - call.startTime.getTime()
    );
    const apiLatency = latencies.reduce((a, b) => a + b, 0) / latencies.length;

    // Get current queue length
    const queueLength = await db.taskQueue.count({
      where: {
        projectId,
        status: 'pending',
      },
    });

    // Calculate resource utilization
    const systemResources = await db.systemResources.findFirst({
      where: {
        projectId,
        timestamp: {
          gte: new Date(Date.now() - 5 * 60 * 1000), // Last 5 minutes
        },
      },
    });

    const resourceUtilization = systemResources ? 
      (systemResources.cpuUsage + systemResources.memoryUsage + systemResources.diskUsage) / 3 : 0;

    // Calculate cost tracking
    const totalCost = recentApiCalls.reduce((sum, call) => sum + call.cost, 0);

    return {
      apiLatency,
      queueLength,
      resourceUtilization,
      costTracking: totalCost,
      historicalData: [], // Will be populated by historicalData service
    };
  } catch (error) {
    console.error('Error calculating system metrics:', error);
    throw error;
  }
} 