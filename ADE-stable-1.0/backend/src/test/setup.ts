import 'reflect-metadata';
import { container } from 'tsyringe';
import { ConfigService } from '../services/config/ConfigService';
import { Logger } from '../services/logger/Logger';

// Mock environment variables for testing
process.env.NODE_ENV = 'test';
process.env.JWT_SECRET = 'test-secret';
process.env.REDIS_URL = 'redis://localhost:6379';
process.env.CORS_ORIGIN = 'http://localhost:3000';
process.env.LOG_LEVEL = 'error';

// Register test dependencies
container.registerSingleton(ConfigService);
container.registerSingleton(Logger);

// Global test timeout
jest.setTimeout(10000);

// Clean up after each test
afterEach(() => {
  jest.clearAllMocks();
});

// Clean up after all tests
afterAll(() => {
  container.clearInstances();
}); 