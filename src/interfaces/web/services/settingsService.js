import axios from 'axios';

const API_BASE_URL = '/api/settings';

const settingsService = {
  // User Profile Settings
  getUserProfileSettings: async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/profile`);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.message || 'Failed to fetch profile settings');
    }
  },

  updateUserProfileSettings: async (data) => {
    try {
      const response = await axios.put(`${API_BASE_URL}/profile`, data);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.message || 'Failed to update profile settings');
    }
  },

  // Appearance Settings
  getAppearanceSettings: async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/appearance`);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.message || 'Failed to fetch appearance settings');
    }
  },

  updateAppearanceSettings: async (data) => {
    try {
      const response = await axios.put(`${API_BASE_URL}/appearance`, data);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.message || 'Failed to update appearance settings');
    }
  },

  // Notification Settings
  getNotificationSettings: async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/notifications`);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.message || 'Failed to fetch notification settings');
    }
  },

  updateNotificationSettings: async (data) => {
    try {
      const response = await axios.put(`${API_BASE_URL}/notifications`, data);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.message || 'Failed to update notification settings');
    }
  },

  // Security Settings
  getSecuritySettings: async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/security`);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.message || 'Failed to fetch security settings');
    }
  },

  updateSecuritySettings: async (data) => {
    try {
      const response = await axios.put(`${API_BASE_URL}/security`, data);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.message || 'Failed to update security settings');
    }
  },

  // System Settings
  getSystemSettings: async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/system`);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.message || 'Failed to fetch system settings');
    }
  },

  updateSystemSettings: async (data) => {
    try {
      const response = await axios.put(`${API_BASE_URL}/system`, data);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.message || 'Failed to update system settings');
    }
  },

  // Integration Settings
  getIntegrationSettings: async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/integrations`);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.message || 'Failed to fetch integration settings');
    }
  },

  updateIntegrationSettings: async (data) => {
    try {
      const response = await axios.put(`${API_BASE_URL}/integrations`, data);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.message || 'Failed to update integration settings');
    }
  },

  // Test Integration Connections
  testIntegration: async (integration, data) => {
    try {
      const response = await axios.post(`${API_BASE_URL}/integrations/${integration}/test`, data);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.message || `Failed to test ${integration} integration`);
    }
  },

  // OAuth Callbacks
  handleOAuthCallback: async (provider, code) => {
    try {
      const response = await axios.post(`${API_BASE_URL}/oauth/${provider}/callback`, { code });
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.message || `Failed to handle ${provider} OAuth callback`);
    }
  },

  // Webhook Configuration
  getWebhookSettings: async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/webhooks`);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.message || 'Failed to fetch webhook settings');
    }
  },

  updateWebhookSettings: async (data) => {
    try {
      const response = await axios.put(`${API_BASE_URL}/webhooks`, data);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.message || 'Failed to update webhook settings');
    }
  },

  // Backup and Restore
  createSettingsBackup: async () => {
    try {
      const response = await axios.post(`${API_BASE_URL}/backup`);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.message || 'Failed to create settings backup');
    }
  },

  restoreSettingsBackup: async (backupId) => {
    try {
      const response = await axios.post(`${API_BASE_URL}/backup/${backupId}/restore`);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.message || 'Failed to restore settings backup');
    }
  },

  // Export and Import
  exportSettings: async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/export`, {
        responseType: 'blob',
      });
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.message || 'Failed to export settings');
    }
  },

  importSettings: async (file) => {
    try {
      const formData = new FormData();
      formData.append('file', file);
      const response = await axios.post(`${API_BASE_URL}/import`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.message || 'Failed to import settings');
    }
  },
};

export default settingsService; 