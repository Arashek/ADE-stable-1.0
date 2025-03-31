import { Redis } from 'ioredis';
import { Mock } from 'jest-mock';

declare module 'ioredis' {
  interface RedisMockFunctions {
    on: Mock<(event: string | symbol, listener: (...args: any[]) => void) => Redis>;
    connect: Mock<() => Promise<void>>;
    disconnect: Mock<() => Promise<void>>;
    quit: Mock<() => Promise<'OK'>>;
    set: Mock<(key: string, value: string | number) => Promise<'OK'>>;
    get: Mock<(key: string) => Promise<string | null>>;
    del: Mock<(key: string) => Promise<number>>;
    incrby: Mock<(key: string, increment: number) => Promise<number>>;
    expire: Mock<(key: string, seconds: number) => Promise<number>>;
    lpush: Mock<(key: string, ...values: string[]) => Promise<number>>;
    ltrim: Mock<(key: string, start: number, stop: number) => Promise<'OK'>>;
    lrange: Mock<(key: string, start: number, stop: number) => Promise<string[]>>;
    keys: Mock<(pattern: string) => Promise<string[]>>;
  }

  interface Redis extends RedisMockFunctions {}
} 