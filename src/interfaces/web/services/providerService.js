import axios from 'axios';

const API_BASE_URL = '/api/providers';

const providerService = {
  // Get all providers
  getProviders: async () => {
    try {
      const response = await axios.get(API_BASE_URL);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.message || 'Failed to fetch providers');
    }
  },

  // Get a specific provider by ID
  getProviderById: async (id) => {
    try {
      const response = await axios.get(`${API_BASE_URL}/${id}`);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.message || 'Failed to fetch provider');
    }
  },

  // Create a new provider
  createProvider: async (providerData) => {
    try {
      const response = await axios.post(API_BASE_URL, providerData);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.message || 'Failed to create provider');
    }
  },

  // Update a provider
  updateProvider: async (id, providerData) => {
    try {
      const response = await axios.put(`${API_BASE_URL}/${id}`, providerData);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.message || 'Failed to update provider');
    }
  },

  // Delete a provider
  deleteProvider: async (id) => {
    try {
      await axios.delete(`${API_BASE_URL}/${id}`);
    } catch (error) {
      throw new Error(error.response?.data?.message || 'Failed to delete provider');
    }
  },

  // Get provider usage statistics
  getProviderUsage: async (id, timeRange) => {
    try {
      const response = await axios.get(`${API_BASE_URL}/${id}/usage`, {
        params: { timeRange },
      });
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.message || 'Failed to fetch usage statistics');
    }
  },

  // Get provider performance data
  getProviderPerformance: async (id, timeRange) => {
    try {
      const response = await axios.get(`${API_BASE_URL}/${id}/performance`, {
        params: { timeRange },
      });
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.message || 'Failed to fetch performance data');
    }
  },

  // Get provider API keys
  getApiKeys: async (id) => {
    try {
      const response = await axios.get(`${API_BASE_URL}/${id}/keys`);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.message || 'Failed to fetch API keys');
    }
  },

  // Add a new API key
  addApiKey: async (id, keyData) => {
    try {
      const response = await axios.post(`${API_BASE_URL}/${id}/keys`, keyData);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.message || 'Failed to add API key');
    }
  },

  // Delete an API key
  deleteApiKey: async (id, keyId) => {
    try {
      await axios.delete(`${API_BASE_URL}/${id}/keys/${keyId}`);
    } catch (error) {
      throw new Error(error.response?.data?.message || 'Failed to delete API key');
    }
  },

  // Rotate an API key
  rotateApiKey: async (id, keyId) => {
    try {
      const response = await axios.post(`${API_BASE_URL}/${id}/keys/${keyId}/rotate`);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.message || 'Failed to rotate API key');
    }
  },

  // Test provider connection
  testConnection: async (id) => {
    try {
      const response = await axios.post(`${API_BASE_URL}/${id}/test`);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.message || 'Failed to test provider connection');
    }
  },

  // Get provider capabilities
  getCapabilities: async (id) => {
    try {
      const response = await axios.get(`${API_BASE_URL}/${id}/capabilities`);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.message || 'Failed to fetch provider capabilities');
    }
  },

  // Update provider settings
  updateSettings: async (id, settings) => {
    try {
      const response = await axios.put(`${API_BASE_URL}/${id}/settings`, settings);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.message || 'Failed to update provider settings');
    }
  },
};

export { providerService }; 