/**
 * Prompt Processing Service for ADE Platform
 * 
 * This service handles prompt processing operations and integrates with the error handling system.
 */

import axios from 'axios';
import { 
  logError, 
  withErrorHandling, 
  ErrorCategory, 
  ErrorSeverity
} from './errorHandling';

// Define interfaces for TypeScript
interface PromptContext {
  [key: string]: any;
}

interface PromptOptions {
  context?: PromptContext;
  pollingInterval?: number;
  timeout?: number;
}

interface PromptStatus {
  status: string;
  message?: string;
  progress?: number;
  result?: any;
  [key: string]: any;
}

interface StatusUpdateCallback {
  (status: PromptStatus): void;
}

// Base URL for prompt API
const API_URL = 'http://localhost:8000';

/**
 * Submit a prompt for processing
 * 
 * @param {string} prompt - The user prompt
 * @param {object} context - Additional context information
 * @returns {Promise} - Promise that resolves with the task ID
 */
const submitPrompt = async (prompt: string, context: PromptContext = {}): Promise<any> => {
  try {
    const response = await axios.post(`${API_URL}/api/prompt`, {
      prompt,
      context
    });
    
    return response.data;
  } catch (error: any) {
    // Log detailed information about the failed prompt submission
    await logError(
      `Failed to submit prompt: ${error.message}`,
      ErrorCategory.API,
      ErrorSeverity.ERROR,
      'promptService',
      {
        promptPreview: prompt.substring(0, 100),
        contextKeys: Object.keys(context),
        statusCode: error.response?.status,
        responseData: error.response?.data
      },
      error.stack
    );
    
    throw error;
  }
};

/**
 * Check the status of a prompt processing task
 * 
 * @param {string} taskId - The task ID
 * @returns {Promise} - Promise that resolves with the task status
 */
const checkPromptStatus = async (taskId: string): Promise<PromptStatus> => {
  try {
    const response = await axios.get(`${API_URL}/api/prompt/${taskId}`);
    return response.data;
  } catch (error: any) {
    // Log error with task ID information
    await logError(
      `Failed to check prompt status: ${error.message}`,
      ErrorCategory.API,
      ErrorSeverity.ERROR,
      'promptService',
      {
        taskId,
        statusCode: error.response?.status,
        responseData: error.response?.data
      },
      error.stack
    );
    
    throw error;
  }
};

/**
 * Periodically poll for prompt processing status until completion or timeout
 * 
 * @param {string} taskId - The task ID
 * @param {number} interval - Polling interval in milliseconds 
 * @param {number} timeout - Maximum time to poll in milliseconds
 * @param {Function} onUpdate - Callback for status updates
 * @returns {Promise} - Promise that resolves with the final status
 */
const pollPromptStatus = async (
  taskId: string, 
  interval: number = 2000, 
  timeout: number = 60000, 
  onUpdate: StatusUpdateCallback | null = null
): Promise<PromptStatus> => {
  const startTime = Date.now();
  
  while (Date.now() - startTime < timeout) {
    try {
      const status = await checkPromptStatus(taskId);
      
      // Call update callback if provided
      if (typeof onUpdate === 'function') {
        onUpdate(status);
      }
      
      // If processing is complete, return the result
      if (status.status === 'completed' || status.status === 'failed') {
        return status;
      }
      
      // Wait for the specified interval
      await new Promise(resolve => setTimeout(resolve, interval));
    } catch (error: any) {
      // Log polling error
      await logError(
        `Error while polling prompt status: ${error.message}`,
        ErrorCategory.API,
        ErrorSeverity.WARNING,
        'promptService',
        {
          taskId,
          elapsedTime: Date.now() - startTime,
          attemptCount: Math.floor((Date.now() - startTime) / interval)
        },
        error.stack
      );
      
      // Continue polling despite errors
      await new Promise(resolve => setTimeout(resolve, interval));
    }
  }
  
  // If we reach here, polling has timed out
  const timeoutError = new Error(`Prompt processing timed out after ${timeout}ms`);
  
  await logError(
    timeoutError.message,
    ErrorCategory.API,
    ErrorSeverity.WARNING,
    'promptService',
    { taskId, timeout }
  );
  
  throw timeoutError;
};

/**
 * Process a prompt from start to finish, handling polling and errors
 * 
 * @param {string} prompt - The user prompt
 * @param {object} options - Processing options
 * @param {Function} onStatusUpdate - Callback for status updates
 * @returns {Promise} - Promise that resolves with the processing result
 */
const processPromptToCompletion = async (
  prompt: string, 
  options: PromptOptions = {}, 
  onStatusUpdate: StatusUpdateCallback | null = null
): Promise<any> => {
  try {
    // Submit the prompt
    const submissionResult = await submitPrompt(prompt, options.context || {});
    const taskId = submissionResult.task_id;
    
    // Notify of initial status
    if (typeof onStatusUpdate === 'function') {
      onStatusUpdate({
        stage: 'submitted',
        taskId,
        status: submissionResult.status,
        message: submissionResult.message
      });
    }
    
    // Poll for completion
    const result = await pollPromptStatus(
      taskId,
      options.pollingInterval || 2000,
      options.timeout || 60000,
      (status) => {
        if (typeof onStatusUpdate === 'function') {
          onStatusUpdate({
            stage: 'processing',
            taskId,
            ...status
          });
        }
      }
    );
    
    // Return the final result
    return {
      stage: 'completed',
      taskId,
      ...result
    };
  } catch (error: any) {
    // Comprehensive error logging for the entire process
    await logError(
      `Complete prompt processing failed: ${error.message}`,
      ErrorCategory.API,
      ErrorSeverity.ERROR,
      'promptService',
      {
        promptPreview: prompt.substring(0, 100),
        options: {
          ...options,
          context: options.context ? Object.keys(options.context) : null
        }
      },
      error.stack
    );
    
    // Return error result
    return {
      stage: 'failed',
      error: error.message,
      details: error.response?.data || null
    };
  }
};

export default {
  submitPrompt: withErrorHandling(submitPrompt, 'promptService.submitPrompt'),
  checkPromptStatus: withErrorHandling(checkPromptStatus, 'promptService.checkPromptStatus'),
  pollPromptStatus,
  processPromptToCompletion
};
