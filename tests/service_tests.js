/**
 * Service Tests for ADE Platform
 * 
 * This file contains tests for the error handling and prompt processing services.
 * Run with Jest or another JavaScript testing framework.
 */

const axios = require('axios');
const MockAdapter = require('axios-mock-adapter');

// Create a mock for axios
const mockAxios = new MockAdapter(axios);

// Import the services to test
// Note: In a real test environment, you'd need to handle the imports appropriately
// based on your testing setup (e.g., Jest, Mocha, etc.)
const errorHandling = require('../frontend/src/services/errorHandling');
const promptService = require('../frontend/src/services/promptService').default;

describe('Error Handling Service', () => {
  beforeEach(() => {
    // Reset axios mock
    mockAxios.reset();
    
    // Setup mock for error logging endpoint
    mockAxios.onPost('http://localhost:8000/api/errors').reply(200, {
      success: true,
      message: 'Error logged successfully'
    });
    
    // Mock localStorage
    global.localStorage = {
      getItem: jest.fn(),
      setItem: jest.fn(),
      removeItem: jest.fn()
    };
    
    // Mock console methods
    console.error = jest.fn();
    console.warn = jest.fn();
  });
  
  test('logError should log errors to the API', async () => {
    const errorMessage = 'Test error message';
    const category = errorHandling.ErrorCategory.FRONTEND;
    const severity = errorHandling.ErrorSeverity.ERROR;
    const component = 'TestComponent';
    const context = { test: true };
    
    await errorHandling.logError(
      errorMessage,
      category,
      severity,
      component,
      context
    );
    
    // Check that the API was called with the correct data
    expect(mockAxios.history.post.length).toBe(1);
    const postedData = JSON.parse(mockAxios.history.post[0].data);
    
    expect(postedData.message).toBe(errorMessage);
    expect(postedData.category).toBe(category);
    expect(postedData.severity).toBe(severity);
    expect(postedData.component).toBe(component);
    expect(postedData.context).toEqual(context);
  });
  
  test('logError should fall back to localStorage when API fails', async () => {
    // Setup mock to fail
    mockAxios.onPost('http://localhost:8000/api/errors').networkError();
    
    const errorMessage = 'Test error message';
    
    await errorHandling.logError(errorMessage);
    
    // Check that localStorage was called
    expect(localStorage.getItem).toHaveBeenCalled();
    expect(localStorage.setItem).toHaveBeenCalled();
    
    // Check that console.error was called
    expect(console.error).toHaveBeenCalled();
  });
  
  test('withErrorHandling should catch and log errors', async () => {
    const testFn = jest.fn().mockImplementation(() => {
      throw new Error('Test error');
    });
    
    const wrappedFn = errorHandling.withErrorHandling(testFn, 'TestFunction');
    
    try {
      await wrappedFn('test');
      fail('Should have thrown an error');
    } catch (error) {
      // Error should be re-thrown after logging
      expect(error.message).toBe('Test error');
    }
    
    // The original function should have been called
    expect(testFn).toHaveBeenCalledWith('test');
    
    // Check that the API was called to log the error
    expect(mockAxios.history.post.length).toBe(1);
  });
});

describe('Prompt Processing Service', () => {
  beforeEach(() => {
    // Reset axios mock
    mockAxios.reset();
    
    // Setup mock for prompt submission endpoint
    mockAxios.onPost('http://localhost:8000/api/prompt').reply(200, {
      task_id: 'test-task-123',
      status: 'submitted',
      message: 'Prompt submitted successfully'
    });
    
    // Setup mock for prompt status endpoint (initial status)
    mockAxios.onGet('http://localhost:8000/api/prompt/test-task-123').reply(200, {
      status: 'processing',
      progress: 0,
      message: 'Processing prompt'
    });
  });
  
  test('submitPrompt should submit a prompt and return task ID', async () => {
    const result = await promptService.submitPrompt('Test prompt', { test: true });
    
    // Check that the API was called with the correct data
    expect(mockAxios.history.post.length).toBe(1);
    const postedData = JSON.parse(mockAxios.history.post[0].data);
    
    expect(postedData.prompt).toBe('Test prompt');
    expect(postedData.context).toEqual({ test: true });
    
    // Check the returned result
    expect(result.task_id).toBe('test-task-123');
    expect(result.status).toBe('submitted');
  });
  
  test('checkPromptStatus should get the status of a task', async () => {
    const result = await promptService.checkPromptStatus('test-task-123');
    
    // Check that the API was called with the correct URL
    expect(mockAxios.history.get.length).toBe(1);
    expect(mockAxios.history.get[0].url).toBe('http://localhost:8000/api/prompt/test-task-123');
    
    // Check the returned result
    expect(result.status).toBe('processing');
    expect(result.progress).toBe(0);
  });
  
  test('pollPromptStatus should poll until completion', async () => {
    // Setup mocks for status changes
    let callCount = 0;
    mockAxios.onGet('http://localhost:8000/api/prompt/test-task-123').reply(() => {
      callCount++;
      
      if (callCount === 1) {
        return [200, {
          status: 'processing',
          progress: 30,
          message: 'Processing prompt'
        }];
      } else if (callCount === 2) {
        return [200, {
          status: 'processing',
          progress: 70,
          message: 'Processing prompt'
        }];
      } else {
        return [200, {
          status: 'completed',
          progress: 100,
          message: 'Processing complete',
          result: {
            code: 'console.log("Hello, world!");',
            description: 'A simple hello world program'
          }
        }];
      }
    });
    
    // Create a mock for setTimeout to speed up the test
    jest.useFakeTimers();
    
    // Create a mock for the update callback
    const updateCallback = jest.fn();
    
    // Start polling (non-blocking)
    const pollPromise = promptService.pollPromptStatus(
      'test-task-123',
      100, // use a short interval
      10000,
      updateCallback
    );
    
    // Fast-forward timers
    jest.advanceTimersByTime(300);
    
    // Wait for the promise to resolve
    const result = await pollPromise;
    
    // Check that the API was called multiple times
    expect(callCount).toBe(3);
    
    // Check that the update callback was called for each status
    expect(updateCallback).toHaveBeenCalledTimes(3);
    
    // Check the final result
    expect(result.status).toBe('completed');
    expect(result.progress).toBe(100);
    expect(result.result.code).toBe('console.log("Hello, world!");');
    
    // Restore timers
    jest.useRealTimers();
  });
  
  test('processPromptToCompletion should handle the full workflow', async () => {
    // Setup mocks for status changes
    let callCount = 0;
    mockAxios.onGet('http://localhost:8000/api/prompt/test-task-123').reply(() => {
      callCount++;
      
      if (callCount === 1) {
        return [200, {
          status: 'analyzing',
          progress: 25,
          message: 'Analyzing requirements'
        }];
      } else if (callCount === 2) {
        return [200, {
          status: 'designing',
          progress: 50,
          message: 'Designing solution'
        }];
      } else if (callCount === 3) {
        return [200, {
          status: 'generating',
          progress: 75,
          message: 'Generating code'
        }];
      } else {
        return [200, {
          status: 'completed',
          progress: 100,
          message: 'Processing complete',
          result: {
            code: 'console.log("Hello, world!");',
            description: 'A simple hello world program'
          }
        }];
      }
    });
    
    // Create a mock for setTimeout to speed up the test
    jest.useFakeTimers();
    
    // Create a mock for the update callback
    const statusUpdateCallback = jest.fn();
    
    // Start processing (non-blocking)
    const processPromise = promptService.processPromptToCompletion(
      'Create a hello world program',
      {
        pollingInterval: 100,
        timeout: 10000
      },
      statusUpdateCallback
    );
    
    // Fast-forward timers
    jest.advanceTimersByTime(500);
    
    // Wait for the promise to resolve
    const result = await processPromise;
    
    // Check the final result
    expect(result.stage).toBe('completed');
    expect(result.status).toBe('completed');
    expect(result.progress).toBe(100);
    
    // Check that the status update callback was called
    expect(statusUpdateCallback).toHaveBeenCalled();
    
    // Restore timers
    jest.useRealTimers();
  });
  
  test('processPromptToCompletion should handle errors', async () => {
    // Setup submission to work
    mockAxios.onPost('http://localhost:8000/api/prompt').reply(200, {
      task_id: 'error-task-123',
      status: 'submitted'
    });
    
    // Setup status check to fail
    mockAxios.onGet('http://localhost:8000/api/prompt/error-task-123').reply(500, {
      error: 'Internal server error'
    });
    
    // Create a mock for the update callback
    const statusUpdateCallback = jest.fn();
    
    // Process the prompt
    const result = await promptService.processPromptToCompletion(
      'This will fail',
      {},
      statusUpdateCallback
    );
    
    // Check that it returned an error result
    expect(result.stage).toBe('failed');
    expect(result.error).toBeTruthy();
    
    // Initial status update should have been called
    expect(statusUpdateCallback).toHaveBeenCalledWith(expect.objectContaining({
      stage: 'submitted'
    }));
  });
});
