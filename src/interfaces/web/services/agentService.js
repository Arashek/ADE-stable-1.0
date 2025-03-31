import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || '/api';

const agentService = {
  // Get list of available agents
  getAgents: async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/agents`);
      return response.data;
    } catch (error) {
      throw new Error('Failed to fetch agents');
    }
  },

  // Get agent details by ID
  getAgentById: async (agentId) => {
    try {
      const response = await axios.get(`${API_BASE_URL}/agents/${agentId}`);
      return response.data;
    } catch (error) {
      throw new Error('Failed to fetch agent details');
    }
  },

  // Send a message to an agent
  sendMessage: async (agentId, { message, type = 'text', attachments = [] }) => {
    try {
      const formData = new FormData();
      formData.append('message', message);
      formData.append('type', type);

      // Append attachments if any
      attachments.forEach((file) => {
        formData.append('attachments', file);
      });

      const response = await axios.post(
        `${API_BASE_URL}/agents/${agentId}/messages`,
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        }
      );
      return response.data;
    } catch (error) {
      throw new Error('Failed to send message to agent');
    }
  },

  // Get chat history with an agent
  getChatHistory: async (agentId) => {
    try {
      const response = await axios.get(`${API_BASE_URL}/agents/${agentId}/messages`);
      return response.data;
    } catch (error) {
      throw new Error('Failed to fetch chat history');
    }
  },

  // Clear chat history with an agent
  clearChatHistory: async (agentId) => {
    try {
      await axios.delete(`${API_BASE_URL}/agents/${agentId}/messages`);
    } catch (error) {
      throw new Error('Failed to clear chat history');
    }
  },

  // Get agent capabilities
  getAgentCapabilities: async (agentId) => {
    try {
      const response = await axios.get(`${API_BASE_URL}/agents/${agentId}/capabilities`);
      return response.data;
    } catch (error) {
      throw new Error('Failed to fetch agent capabilities');
    }
  },

  // Update agent settings
  updateAgentSettings: async (agentId, settings) => {
    try {
      const response = await axios.patch(
        `${API_BASE_URL}/agents/${agentId}/settings`,
        settings
      );
      return response.data;
    } catch (error) {
      throw new Error('Failed to update agent settings');
    }
  },

  // Get agent status
  getAgentStatus: async (agentId) => {
    try {
      const response = await axios.get(`${API_BASE_URL}/agents/${agentId}/status`);
      return response.data;
    } catch (error) {
      throw new Error('Failed to fetch agent status');
    }
  },

  // Initialize agent with specific configuration
  initializeAgent: async (agentId, config) => {
    try {
      const response = await axios.post(
        `${API_BASE_URL}/agents/${agentId}/initialize`,
        config
      );
      return response.data;
    } catch (error) {
      throw new Error('Failed to initialize agent');
    }
  },

  // Terminate agent session
  terminateAgent: async (agentId) => {
    try {
      await axios.post(`${API_BASE_URL}/agents/${agentId}/terminate`);
    } catch (error) {
      throw new Error('Failed to terminate agent');
    }
  },
};

export { agentService }; 