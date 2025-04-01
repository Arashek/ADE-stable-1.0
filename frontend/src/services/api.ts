import axios from 'axios';
import { errorLoggingService, ErrorCategory } from './error-logging.service';

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000';

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add request interceptor for authentication
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Add response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    // Log API errors using the error logging service
    const endpoint = error.config?.url || 'unknown';
    const requestData = error.config?.data ? JSON.parse(error.config.data) : undefined;
    
    // Extract the error message from the response
    const errorMessage = error.response?.data?.detail || 
                         error.response?.data?.message || 
                         error.message || 
                         'Unknown API error';
    
    // Determine error category based on status code
    let category = ErrorCategory.API;
    if (error.response?.status === 401 || error.response?.status === 403) {
      category = ErrorCategory.AUTHENTICATION;
    } else if (error.response?.status === 422) {
      category = ErrorCategory.VALIDATION;
    } else if (!error.response && error.request) {
      category = ErrorCategory.NETWORK;
    }
    
    // Log the error
    errorLoggingService.logApiError(
      new Error(errorMessage),
      endpoint,
      requestData
    );
    
    if (error.response?.status === 401) {
      // Handle unauthorized access
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default api;