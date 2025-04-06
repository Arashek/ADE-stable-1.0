export const API_CONFIG = {
  BASE_URL: process.env.REACT_APP_API_URL || "http://localhost:8003",
  ENDPOINTS: {
    HEALTH: "/api/health",
    PROCESS_PROMPT: "/api/process_prompt",
    STATUS: "/api/status"
  }
};
