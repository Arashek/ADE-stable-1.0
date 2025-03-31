import { QualityMetrics } from '../types/performance';
import { db } from '../db';

export async function calculateQualityMetrics(projectId: string): Promise<QualityMetrics> {
  try {
    // Get recent code quality assessments
    const recentAssessments = await db.codeAssessments.findMany({
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

    // Calculate code quality score
    const latestAssessment = recentAssessments[0];
    const codeQualityScore = latestAssessment ? 
      (latestAssessment.complexityScore + latestAssessment.maintainabilityScore + latestAssessment.reliabilityScore) / 3 : 0;

    // Calculate test coverage
    const testCoverage = latestAssessment ? latestAssessment.testCoverage : 0;

    // Calculate documentation completeness
    const documentationCompleteness = latestAssessment ? 
      (latestAssessment.apiDocsScore + latestAssessment.codeCommentsScore + latestAssessment.readmeScore) / 3 : 0;

    // Calculate error prevention rate
    const totalPotentialIssues = recentAssessments.reduce((sum, assessment) => 
      sum + assessment.potentialIssues, 0
    );
    const preventedIssues = recentAssessments.reduce((sum, assessment) => 
      sum + assessment.preventedIssues, 0
    );
    const errorPreventionRate = (preventedIssues / totalPotentialIssues) * 100;

    return {
      codeQualityScore,
      testCoverage,
      documentationCompleteness,
      errorPreventionRate,
      historicalData: [], // Will be populated by historicalData service
    };
  } catch (error) {
    console.error('Error calculating quality metrics:', error);
    throw error;
  }
} 