import { TextEncoder, TextDecoder } from 'util';
import { jest } from '@jest/globals';
import { WebSocket } from 'ws';
import Redis from 'ioredis';

// Add TextEncoder and TextDecoder to global scope for Node.js environment
global.TextEncoder = TextEncoder;
global.TextDecoder = TextDecoder as any;

// Define the type for our mock Redis instance
type MockRedisInstance = {
  connect: jest.Mock<Promise<void>>;
  disconnect: jest.Mock<Promise<void>>;
  quit: jest.Mock<Promise<string>>;
  set: jest.Mock<Promise<string>>;
  get: jest.Mock<Promise<string | null>>;
  del: jest.Mock<Promise<number>>;
  incrby: jest.Mock<Promise<number>>;
  expire: jest.Mock<Promise<number>>;
  lpush: jest.Mock<Promise<number>>;
  ltrim: jest.Mock<Promise<string>>;
  lrange: jest.Mock<Promise<string[]>>;
  keys: jest.Mock<Promise<string[]>>;
  on: jest.Mock<MockRedisInstance>;
  _errorCallback: Function | null;
};

// Mock Redis
jest.mock('ioredis', () => {
  const RedisMock = jest.fn().mockImplementation((): MockRedisInstance => {
    const instance: MockRedisInstance = {
      connect: jest.fn().mockResolvedValue(undefined),
      disconnect: jest.fn().mockResolvedValue(undefined),
      quit: jest.fn().mockResolvedValue('OK'),
      set: jest.fn().mockResolvedValue('OK'),
      get: jest.fn().mockResolvedValue(null),
      del: jest.fn().mockResolvedValue(1),
      incrby: jest.fn().mockResolvedValue(1),
      expire: jest.fn().mockResolvedValue(1),
      lpush: jest.fn().mockResolvedValue(1),
      ltrim: jest.fn().mockResolvedValue('OK'),
      lrange: jest.fn().mockResolvedValue([]),
      keys: jest.fn().mockResolvedValue([]),
      on: jest.fn().mockImplementation((event: string, listener: Function): MockRedisInstance => {
        if (event === 'error') {
          instance._errorCallback = listener;
        }
        return instance;
      }),
      _errorCallback: null
    };
    return instance;
  });

  return RedisMock;
});

// Mock WebSocket
jest.mock('ws', () => {
  return {
    WebSocket: jest.fn().mockImplementation(() => ({
      on: jest.fn(),
      send: jest.fn(),
      close: jest.fn()
    }))
  };
});

// Mock jsonwebtoken
jest.mock('jsonwebtoken', () => ({
  verify: jest.fn().mockReturnValue({ userId: 'test-user' }),
  sign: jest.fn().mockReturnValue('test-token')
}));

// Add global.gc if it doesn't exist (for memory tests)
if (!global.gc) {
  global.gc = async () => {
    return Promise.resolve();
  };
}

// Increase timeout for performance tests
jest.setTimeout(30000);

// Clear all mocks after each test
afterEach(() => {
  jest.clearAllMocks();
}); 