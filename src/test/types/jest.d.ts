import { jest } from '@jest/globals';

declare module '@jest/globals' {
  interface Mock<T = any, Y extends any[] = any> {
    mockReturnValue(value: T): this;
    mockResolvedValue(value: T): this;
    mockRejectedValue(value: any): this;
    mockImplementation(fn: (...args: Y) => T): this;
  }
} 