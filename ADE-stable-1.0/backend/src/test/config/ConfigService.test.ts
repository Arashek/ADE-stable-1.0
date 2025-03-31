import { container } from 'tsyringe';
import { ConfigService } from '../../services/config/ConfigService';

describe('ConfigService', () => {
  let configService: ConfigService;

  beforeEach(() => {
    // Clear environment variables before each test
    process.env = {};
    
    // Set test environment variables
    process.env.TEST_STRING = 'test-value';
    process.env.TEST_NUMBER = '42';
    process.env.TEST_BOOLEAN = 'true';
    process.env.TEST_ARRAY = 'item1,item2,item3';
    
    configService = container.resolve(ConfigService);
  });

  afterEach(() => {
    container.clearInstances();
  });

  describe('get', () => {
    it('should return string value for existing key', () => {
      expect(configService.get('TEST_STRING')).toBe('test-value');
    });

    it('should throw error for non-existent key', () => {
      expect(() => configService.get('NON_EXISTENT')).toThrow('Configuration key NON_EXISTENT not found');
    });
  });

  describe('getOptional', () => {
    it('should return string value for existing key', () => {
      expect(configService.getOptional('TEST_STRING')).toBe('test-value');
    });

    it('should return undefined for non-existent key', () => {
      expect(configService.getOptional('NON_EXISTENT')).toBeUndefined();
    });
  });

  describe('getNumber', () => {
    it('should return number value for valid number string', () => {
      expect(configService.getNumber('TEST_NUMBER')).toBe(42);
    });

    it('should throw error for invalid number string', () => {
      process.env.INVALID_NUMBER = 'not-a-number';
      expect(() => configService.getNumber('INVALID_NUMBER')).toThrow('Configuration key INVALID_NUMBER is not a valid number');
    });

    it('should throw error for non-existent key', () => {
      expect(() => configService.getNumber('NON_EXISTENT')).toThrow('Configuration key NON_EXISTENT not found');
    });
  });

  describe('getBoolean', () => {
    it('should return true for "true" string', () => {
      expect(configService.getBoolean('TEST_BOOLEAN')).toBe(true);
    });

    it('should return false for "false" string', () => {
      process.env.TEST_BOOLEAN = 'false';
      expect(configService.getBoolean('TEST_BOOLEAN')).toBe(false);
    });

    it('should throw error for invalid boolean string', () => {
      process.env.INVALID_BOOLEAN = 'not-a-boolean';
      expect(() => configService.getBoolean('INVALID_BOOLEAN')).toThrow('Configuration key INVALID_BOOLEAN is not a valid boolean');
    });

    it('should throw error for non-existent key', () => {
      expect(() => configService.getBoolean('NON_EXISTENT')).toThrow('Configuration key NON_EXISTENT not found');
    });
  });

  describe('getArray', () => {
    it('should return array of strings for comma-separated string', () => {
      expect(configService.getArray('TEST_ARRAY')).toEqual(['item1', 'item2', 'item3']);
    });

    it('should handle empty array', () => {
      process.env.EMPTY_ARRAY = '';
      expect(configService.getArray('EMPTY_ARRAY')).toEqual(['']);
    });

    it('should throw error for non-existent key', () => {
      expect(() => configService.getArray('NON_EXISTENT')).toThrow('Configuration key NON_EXISTENT not found');
    });
  });

  describe('set', () => {
    it('should set new configuration value', () => {
      configService.set('NEW_KEY', 'new-value');
      expect(configService.get('NEW_KEY')).toBe('new-value');
      expect(process.env.NEW_KEY).toBe('new-value');
    });

    it('should update existing configuration value', () => {
      configService.set('TEST_STRING', 'updated-value');
      expect(configService.get('TEST_STRING')).toBe('updated-value');
      expect(process.env.TEST_STRING).toBe('updated-value');
    });
  });

  describe('has', () => {
    it('should return true for existing key', () => {
      expect(configService.has('TEST_STRING')).toBe(true);
    });

    it('should return false for non-existent key', () => {
      expect(configService.has('NON_EXISTENT')).toBe(false);
    });
  });

  describe('getAll', () => {
    it('should return all configuration values', () => {
      const allConfig = configService.getAll();
      expect(allConfig).toEqual({
        TEST_STRING: 'test-value',
        TEST_NUMBER: '42',
        TEST_BOOLEAN: 'true',
        TEST_ARRAY: 'item1,item2,item3'
      });
    });

    it('should return empty object when no configuration exists', () => {
      process.env = {};
      expect(configService.getAll()).toEqual({});
    });
  });
}); 