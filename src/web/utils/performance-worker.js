// Web Worker for performance monitoring
self.onmessage = function(e) {
  const { type, data } = e.data;

  switch (type) {
    case 'calculateStats':
      const stats = calculateStatistics(data);
      self.postMessage({ type: 'stats', data: stats });
      break;

    case 'analyzePerformance':
      const analysis = analyzePerformanceData(data);
      self.postMessage({ type: 'analysis', data: analysis });
      break;

    case 'detectAnomalies':
      const anomalies = detectAnomalies(data);
      self.postMessage({ type: 'anomalies', data: anomalies });
      break;

    default:
      self.postMessage({ type: 'error', error: 'Unknown message type' });
  }
};

// Calculate statistical measures
function calculateStatistics(data) {
  const values = data.map(d => d.value);
  const sorted = [...values].sort((a, b) => a - b);
  
  return {
    mean: calculateMean(values),
    median: calculateMedian(sorted),
    stdDev: calculateStandardDeviation(values),
    percentiles: {
      p50: calculatePercentile(sorted, 50),
      p75: calculatePercentile(sorted, 75),
      p90: calculatePercentile(sorted, 90),
      p95: calculatePercentile(sorted, 95),
      p99: calculatePercentile(sorted, 99)
    },
    min: Math.min(...values),
    max: Math.max(...values)
  };
}

// Calculate mean
function calculateMean(values) {
  return values.reduce((sum, val) => sum + val, 0) / values.length;
}

// Calculate median
function calculateMedian(sorted) {
  const mid = Math.floor(sorted.length / 2);
  if (sorted.length % 2 === 0) {
    return (sorted[mid - 1] + sorted[mid]) / 2;
  }
  return sorted[mid];
}

// Calculate standard deviation
function calculateStandardDeviation(values) {
  const mean = calculateMean(values);
  const squareDiffs = values.map(value => {
    const diff = value - mean;
    return diff * diff;
  });
  const avgSquareDiff = calculateMean(squareDiffs);
  return Math.sqrt(avgSquareDiff);
}

// Calculate percentile
function calculatePercentile(sorted, percentile) {
  const index = Math.ceil((percentile / 100) * sorted.length) - 1;
  return sorted[index];
}

// Analyze performance data
function analyzePerformanceData(data) {
  const stats = calculateStatistics(data);
  const anomalies = detectAnomalies(data);
  
  return {
    statistics: stats,
    anomalies,
    recommendations: generateRecommendations(stats, anomalies)
  };
}

// Detect anomalies in performance data
function detectAnomalies(data) {
  const stats = calculateStatistics(data);
  const threshold = stats.stdDev * 2; // 2 standard deviations

  return data.filter(d => {
    const diff = Math.abs(d.value - stats.mean);
    return diff > threshold;
  });
}

// Generate performance recommendations
function generateRecommendations(stats, anomalies) {
  const recommendations = [];

  // Check for high latency
  if (stats.p95 > 1000) { // 1 second
    recommendations.push({
      type: 'latency',
      message: 'High latency detected. Consider optimizing performance.',
      severity: 'high'
    });
  }

  // Check for memory issues
  if (stats.mean > 100 * 1024 * 1024) { // 100MB
    recommendations.push({
      type: 'memory',
      message: 'High memory usage detected. Consider implementing memory optimizations.',
      severity: 'medium'
    });
  }

  // Check for anomalies
  if (anomalies.length > 0) {
    recommendations.push({
      type: 'anomaly',
      message: `${anomalies.length} performance anomalies detected.`,
      severity: 'high'
    });
  }

  return recommendations;
} 