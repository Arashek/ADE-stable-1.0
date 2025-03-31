import { AgentMetrics } from '../types/performance';
import { db } from '../db';

export async function calculateAgentMetrics(projectId: string): Promise<AgentMetrics> {
  try {
    // Get recent agent activities
    const recentActivities = await db.agentActivities.findMany({
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

    // Calculate task completion rate
    const totalTasks = recentActivities.filter(a => a.type === 'task').length;
    const completedTasks = recentActivities.filter(a => 
      a.type === 'task' && a.status === 'completed'
    ).length;
    const taskCompletionRate = (completedTasks / totalTasks) * 100;

    // Calculate error recovery rate
    const totalErrors = recentActivities.filter(a => a.type === 'error').length;
    const recoveredErrors = recentActivities.filter(a => 
      a.type === 'error' && a.status === 'recovered'
    ).length;
    const errorRecoveryRate = (recoveredErrors / totalErrors) * 100;

    // Calculate coordination efficiency
    const coordinationActivities = recentActivities.filter(a => a.type === 'coordination');
    const successfulCoordinations = coordinationActivities.filter(a => a.status === 'success').length;
    const coordinationEfficiency = (successfulCoordinations / coordinationActivities.length) * 100;

    // Calculate resource usage
    const resourceUsage = recentActivities.reduce((sum, activity) => 
      sum + (activity.resourceUsage || 0), 0
    ) / recentActivities.length;

    return {
      taskCompletionRate,
      errorRecoveryRate,
      coordinationEfficiency,
      resourceUsage,
      historicalData: [], // Will be populated by historicalData service
    };
  } catch (error) {
    console.error('Error calculating agent metrics:', error);
    throw error;
  }
} 