import { useState } from 'react';
import axios from 'axios';
import { DesignRequest, DesignResponse, DesignFeedback } from '../types/design';

const API_BASE_URL = process.env.REACT_APP_API_URL || '';

export const useDesignAgent = () => {
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const generateMockup = async (request: DesignRequest): Promise<DesignResponse> => {
        setLoading(true);
        setError(null);
        try {
            const response = await axios.post<DesignResponse>(
                `${API_BASE_URL}/api/design/mockup`,
                request
            );
            return response.data;
        } catch (err) {
            const message = err instanceof Error ? err.message : 'Failed to generate mockup';
            setError(message);
            throw err;
        } finally {
            setLoading(false);
        }
    };

    const analyzeDesign = async (design: any): Promise<DesignFeedback> => {
        setLoading(true);
        setError(null);
        try {
            const response = await axios.post<DesignFeedback>(
                `${API_BASE_URL}/api/design/analyze`,
                { design }
            );
            return response.data;
        } catch (err) {
            const message = err instanceof Error ? err.message : 'Failed to analyze design';
            setError(message);
            throw err;
        } finally {
            setLoading(false);
        }
    };

    const generateAssets = async (request: DesignRequest): Promise<string[]> => {
        setLoading(true);
        setError(null);
        try {
            const response = await axios.post<{ assets: string[] }>(
                `${API_BASE_URL}/api/design/assets`,
                request
            );
            return response.data.assets;
        } catch (err) {
            const message = err instanceof Error ? err.message : 'Failed to generate assets';
            setError(message);
            throw err;
        } finally {
            setLoading(false);
        }
    };

    const getCacheStats = async () => {
        try {
            const response = await axios.get(
                `${API_BASE_URL}/api/design/cache/stats`
            );
            return response.data;
        } catch (err) {
            const message = err instanceof Error ? err.message : 'Failed to get cache stats';
            setError(message);
            throw err;
        }
    };

    const clearCache = async () => {
        try {
            await axios.post(`${API_BASE_URL}/api/design/cache/clear`);
        } catch (err) {
            const message = err instanceof Error ? err.message : 'Failed to clear cache';
            setError(message);
            throw err;
        }
    };

    return {
        generateMockup,
        analyzeDesign,
        generateAssets,
        getCacheStats,
        clearCache,
        loading,
        error,
    };
}; 