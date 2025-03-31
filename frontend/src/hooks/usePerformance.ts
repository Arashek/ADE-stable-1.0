import { useState, useEffect } from 'react';
import { performanceMonitor } from '../services/performance';

interface PerformanceMetric {
  name: string;
  value: number;
  timestamp: number;
}

interface UsePerformanceOptions {
  metricNames?: string[];
  timeWindow?: number;
}

interface UsePerformanceResult {
  metrics: PerformanceMetric[];
  averages: { [key: string]: number };
  clearMetrics: () => void;
  recordMetric: (name: string, value: number) => void;
}

export const usePerformance = (options: UsePerformanceOptions = {}): UsePerformanceResult => {
  const { metricNames, timeWindow = 60000 } = options;
  const [metrics, setMetrics] = useState<PerformanceMetric[]>([]);
  const [averages, setAverages] = useState<{ [key: string]: number }>({});

  useEffect(() => {
    const unsubscribe = performanceMonitor.subscribe((newMetrics) => {
      const filteredMetrics = metricNames
        ? newMetrics.filter(metric => metricNames.includes(metric.name))
        : newMetrics;
      
      setMetrics(filteredMetrics);
      
      // Calculate averages for specified metrics
      const newAverages: { [key: string]: number } = {};
      if (metricNames) {
        metricNames.forEach(name => {
          newAverages[name] = performanceMonitor.getAverageMetric(name, timeWindow);
        });
      }
      setAverages(newAverages);
    });

    return () => {
      unsubscribe();
    };
  }, [metricNames, timeWindow]);

  const clearMetrics = () => {
    performanceMonitor.clearMetrics();
  };

  const recordMetric = (name: string, value: number) => {
    performanceMonitor.recordMetric(name, value);
  };

  return {
    metrics,
    averages,
    clearMetrics,
    recordMetric
  };
};

// Example usage:
/*
const MyComponent = () => {
  const { metrics, averages, recordMetric } = usePerformance({
    metricNames: ['page-load', 'ttfb'],
    timeWindow: 5 * 60 * 1000 // 5 minutes
  });

  useEffect(() => {
    // Record a custom metric
    recordMetric('custom-operation', 150);
  }, []);

  return (
    <div>
      <p>Average TTFB: {averages['ttfb']}ms</p>
      <p>Average Page Load: {averages['page-load']}ms</p>
    </div>
  );
};
*/ 