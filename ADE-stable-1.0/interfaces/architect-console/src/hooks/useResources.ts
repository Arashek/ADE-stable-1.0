import { useState, useEffect } from 'react';
import useStore from '../store';
import { resourceApi } from '../services/api';
import { ResourceData } from '../types';

export const useResources = () => {
  const { resourceData, addResourceData, clearResourceData } = useStore();
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadInitialData = async () => {
      try {
        setIsLoading(true);
        const fetchedData = await resourceApi.getResourceData();
        clearResourceData();
        fetchedData.forEach(addResourceData);
      } catch (err) {
        setError('Failed to load resource data');
        console.error('Error loading resource data:', err);
      } finally {
        setIsLoading(false);
      }
    };

    loadInitialData();
  }, [clearResourceData, addResourceData]);

  useEffect(() => {
    const unsubscribe = resourceApi.subscribeToResourceUpdates((data) => {
      addResourceData(data);
    });

    return () => {
      unsubscribe();
    };
  }, [addResourceData]);

  const getLatestData = () => {
    if (resourceData.length === 0) return null;
    return resourceData[resourceData.length - 1];
  };

  const getDataForTimeRange = (minutes: number) => {
    const now = new Date();
    return resourceData.filter((data) => {
      const dataTime = new Date(data.time);
      return now.getTime() - dataTime.getTime() <= minutes * 60 * 1000;
    });
  };

  return {
    resourceData,
    isLoading,
    error,
    getLatestData,
    getDataForTimeRange,
  };
}; 