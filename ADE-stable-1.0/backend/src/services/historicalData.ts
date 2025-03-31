import { HistoricalData } from '../types/performance';
import { db } from '../db';

export async function getHistoricalData(
  projectId: string,
  timeRange: string
): Promise<HistoricalData> {
  try {
    // Calculate time window based on range
    const now = new Date();
    let startTime: Date;
    let interval: number;

    switch (timeRange) {
      case '1h':
        startTime = new Date(now.getTime() - 60 * 60 * 1000);
        interval = 5 * 60 * 1000; // 5 minutes
        break;
      case '24h':
        startTime = new Date(now.getTime() - 24 * 60 * 60 * 1000);
        interval = 30 * 60 * 1000; // 30 minutes
        break;
      case '7d':
        startTime = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);
        interval = 2 * 60 * 60 * 1000; // 2 hours
        break;
      case '30d':
        startTime = new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000);
        interval = 6 * 60 * 60 * 1000; // 6 hours
        break;
      default:
        throw new Error('Invalid time range');
    }

    // Generate time points
    const timePoints = [];
    for (let t = startTime; t <= now; t = new Date(t.getTime() + interval)) {
      timePoints.push(t);
    }

    // Fetch historical data for each metric type
    const modelData = await fetchModelHistoricalData(projectId, timePoints);
    const agentData = await fetchAgentHistoricalData(projectId, timePoints);
    const systemData = await fetchSystemHistoricalData(projectId, timePoints);
    const qualityData = await fetchQualityHistoricalData(projectId, timePoints);

    return {
      model: modelData,
      agent: agentData,
      system: systemData,
      quality: qualityData,
    };
  } catch (error) {
    console.error('Error fetching historical data:', error);
    throw error;
  }
}

async function fetchModelHistoricalData(projectId: string, timePoints: Date[]) {
  const data = [];
  for (const timePoint of timePoints) {
    const interactions = await db.modelInteractions.findMany({
      where: {
        projectId,
        timestamp: {
          gte: new Date(timePoint.getTime() - 5 * 60 * 1000), // 5 minutes before
          lte: timePoint,
        },
      },
    });

    if (interactions.length > 0) {
      data.push({
        timestamp: timePoint.toISOString(),
        responseTime: interactions.reduce((sum, i) => 
          sum + (i.endTime.getTime() - i.startTime.getTime()), 0
        ) / interactions.length,
        successRate: (interactions.filter(i => i.status === 'success').length / interactions.length) * 100,
        errorRate: (interactions.filter(i => i.status === 'error').length / interactions.length) * 100,
        tokenUsage: interactions.reduce((sum, i) => sum + i.tokenUsage, 0),
        costPerRequest: interactions.reduce((sum, i) => sum + i.cost, 0) / interactions.length,
      });
    }
  }
  return data;
}

async function fetchAgentHistoricalData(projectId: string, timePoints: Date[]) {
  const data = [];
  for (const timePoint of timePoints) {
    const activities = await db.agentActivities.findMany({
      where: {
        projectId,
        timestamp: {
          gte: new Date(timePoint.getTime() - 5 * 60 * 1000),
          lte: timePoint,
        },
      },
    });

    if (activities.length > 0) {
      const tasks = activities.filter(a => a.type === 'task');
      const errors = activities.filter(a => a.type === 'error');
      const coordinations = activities.filter(a => a.type === 'coordination');

      data.push({
        timestamp: timePoint.toISOString(),
        taskCompletionRate: (tasks.filter(a => a.status === 'completed').length / tasks.length) * 100,
        errorRecoveryRate: (errors.filter(a => a.status === 'recovered').length / errors.length) * 100,
        coordinationEfficiency: (coordinations.filter(a => a.status === 'success').length / coordinations.length) * 100,
        resourceUsage: activities.reduce((sum, a) => sum + (a.resourceUsage || 0), 0) / activities.length,
      });
    }
  }
  return data;
}

async function fetchSystemHistoricalData(projectId: string, timePoints: Date[]) {
  const data = [];
  for (const timePoint of timePoints) {
    const apiCalls = await db.apiCalls.findMany({
      where: {
        projectId,
        timestamp: {
          gte: new Date(timePoint.getTime() - 5 * 60 * 1000),
          lte: timePoint,
        },
      },
    });

    const resources = await db.systemResources.findFirst({
      where: {
        projectId,
        timestamp: {
          gte: new Date(timePoint.getTime() - 5 * 60 * 1000),
          lte: timePoint,
        },
      },
    });

    if (apiCalls.length > 0 || resources) {
      data.push({
        timestamp: timePoint.toISOString(),
        apiLatency: apiCalls.reduce((sum, call) => 
          sum + (call.endTime.getTime() - call.startTime.getTime()), 0
        ) / apiCalls.length,
        queueLength: await db.taskQueue.count({
          where: {
            projectId,
            status: 'pending',
            timestamp: {
              lte: timePoint,
            },
          },
        }),
        resourceUtilization: resources ? 
          (resources.cpuUsage + resources.memoryUsage + resources.diskUsage) / 3 : 0,
        costTracking: apiCalls.reduce((sum, call) => sum + call.cost, 0),
      });
    }
  }
  return data;
}

async function fetchQualityHistoricalData(projectId: string, timePoints: Date[]) {
  const data = [];
  for (const timePoint of timePoints) {
    const assessments = await db.codeAssessments.findMany({
      where: {
        projectId,
        timestamp: {
          gte: new Date(timePoint.getTime() - 5 * 60 * 1000),
          lte: timePoint,
        },
      },
    });

    if (assessments.length > 0) {
      const latestAssessment = assessments[0];
      data.push({
        timestamp: timePoint.toISOString(),
        codeQualityScore: (latestAssessment.complexityScore + 
          latestAssessment.maintainabilityScore + 
          latestAssessment.reliabilityScore) / 3,
        testCoverage: latestAssessment.testCoverage,
        documentationCompleteness: (latestAssessment.apiDocsScore + 
          latestAssessment.codeCommentsScore + 
          latestAssessment.readmeScore) / 3,
        errorPreventionRate: (latestAssessment.preventedIssues / 
          latestAssessment.potentialIssues) * 100,
      });
    }
  }
  return data;
} 