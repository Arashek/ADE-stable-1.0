import { container } from 'tsyringe';
import { Logger } from '../../services/logger/Logger';
import { ConfigService } from '../../services/config/ConfigService';
import winston from 'winston';

jest.mock('winston', () => {
  const mFormat = {
    combine: jest.fn(),
    timestamp: jest.fn(),
    json: jest.fn(),
    colorize: jest.fn(),
    simple: jest.fn()
  };

  const mTransports = {
    Console: jest.fn(),
    File: jest.fn()
  };

  return {
    format: mFormat,
    transports: mTransports,
    createLogger: jest.fn().mockReturnValue({
      info: jest.fn(),
      error: jest.fn(),
      warn: jest.fn(),
      debug: jest.fn(),
      verbose: jest.fn()
    })
  };
});

describe('Logger', () => {
  let logger: Logger;
  let configService: ConfigService;
  let winstonLogger: any;

  beforeEach(() => {
    // Reset all mocks
    jest.clearAllMocks();

    // Mock ConfigService
    configService = {
      get: jest.fn().mockReturnValue('info')
    } as any;

    // Create logger instance
    logger = new Logger(configService);
    winstonLogger = (winston as any).createLogger();
  });

  afterEach(() => {
    container.clearInstances();
  });

  describe('constructor', () => {
    it('should create winston logger with correct configuration', () => {
      expect(winston.createLogger).toHaveBeenCalledWith({
        level: 'info',
        format: expect.any(Object),
        transports: expect.any(Array)
      });
    });

    it('should use log level from config', () => {
      configService.get = jest.fn().mockReturnValue('debug');
      new Logger(configService);
      expect(winston.createLogger).toHaveBeenCalledWith(
        expect.objectContaining({
          level: 'debug'
        })
      );
    });
  });

  describe('info', () => {
    it('should call winston logger info method', () => {
      const message = 'Test info message';
      const meta = { test: 'data' };
      logger.info(message, meta);
      expect(winstonLogger.info).toHaveBeenCalledWith(message, meta);
    });
  });

  describe('error', () => {
    it('should call winston logger error method', () => {
      const message = 'Test error message';
      const meta = { test: 'data' };
      logger.error(message, meta);
      expect(winstonLogger.error).toHaveBeenCalledWith(message, meta);
    });
  });

  describe('warn', () => {
    it('should call winston logger warn method', () => {
      const message = 'Test warning message';
      const meta = { test: 'data' };
      logger.warn(message, meta);
      expect(winstonLogger.warn).toHaveBeenCalledWith(message, meta);
    });
  });

  describe('debug', () => {
    it('should call winston logger debug method', () => {
      const message = 'Test debug message';
      const meta = { test: 'data' };
      logger.debug(message, meta);
      expect(winstonLogger.debug).toHaveBeenCalledWith(message, meta);
    });
  });

  describe('verbose', () => {
    it('should call winston logger verbose method', () => {
      const message = 'Test verbose message';
      const meta = { test: 'data' };
      logger.verbose(message, meta);
      expect(winstonLogger.verbose).toHaveBeenCalledWith(message, meta);
    });
  });

  describe('log levels', () => {
    it('should respect log level configuration', () => {
      configService.get = jest.fn().mockReturnValue('error');
      logger = new Logger(configService);
      
      logger.info('info message');
      logger.warn('warn message');
      logger.debug('debug message');
      logger.verbose('verbose message');
      
      expect(winstonLogger.info).not.toHaveBeenCalled();
      expect(winstonLogger.warn).not.toHaveBeenCalled();
      expect(winstonLogger.debug).not.toHaveBeenCalled();
      expect(winstonLogger.verbose).not.toHaveBeenCalled();
    });
  });
}); 