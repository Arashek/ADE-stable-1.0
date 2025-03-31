import { SecurityAuditLogger, SecurityEventType } from '../SecurityAuditLogger';
import { Logger } from '../../../logging/Logger';
import { writeFile, readFile, stat } from 'fs/promises';
import { join } from 'path';

jest.mock('../../../logging/Logger');
jest.mock('fs/promises');

describe('SecurityAuditLogger', () => {
  let auditLogger: SecurityAuditLogger;
  let mockWriteFile: jest.MockedFunction<typeof writeFile>;
  let mockReadFile: jest.MockedFunction<typeof readFile>;
  let mockStat: jest.MockedFunction<typeof stat>;
  let mockLogger: jest.Mocked<Logger>;

  beforeEach(() => {
    jest.clearAllMocks();
    auditLogger = new SecurityAuditLogger('/test/log/path');
    mockWriteFile = writeFile as jest.MockedFunction<typeof writeFile>;
    mockReadFile = readFile as jest.MockedFunction<typeof readFile>;
    mockStat = stat as jest.MockedFunction<typeof stat>;
    mockLogger = new Logger('test') as jest.Mocked<Logger>;
  });

  describe('logEvent', () => {
    it('should log a security event successfully', async () => {
      const event = {
        eventType: SecurityEventType.POLICY_CHANGE,
        containerId: 'test-container',
        userId: 'test-user',
        action: 'test-action',
        details: { test: 'data' },
        severity: 'high' as const,
      };

      mockWriteFile.mockResolvedValue(undefined);
      mockStat.mockResolvedValue({ size: 0 } as any);

      await auditLogger.logEvent(event);

      expect(mockWriteFile).toHaveBeenCalledWith(
        expect.stringContaining('security-audit.log'),
        expect.stringContaining(JSON.stringify(event))
      );
      expect(mockLogger.info).toHaveBeenCalledWith(
        expect.stringContaining('Security event logged')
      );
    });

    it('should handle errors when logging events', async () => {
      const event = {
        eventType: SecurityEventType.POLICY_CHANGE,
        containerId: 'test-container',
        userId: 'test-user',
        action: 'test-action',
        details: { test: 'data' },
        severity: 'high' as const,
      };

      const error = new Error('Failed to write log');
      mockWriteFile.mockRejectedValue(error);

      await expect(auditLogger.logEvent(event)).rejects.toThrow(error);
      expect(mockLogger.error).toHaveBeenCalledWith(
        'Failed to log security event',
        error
      );
    });
  });

  describe('getAuditLogs', () => {
    it('should retrieve and filter audit logs', async () => {
      const mockLogs = [
        {
          timestamp: '2024-01-01T00:00:00Z',
          eventType: SecurityEventType.POLICY_CHANGE,
          containerId: 'container1',
          userId: 'user1',
          action: 'action1',
          details: {},
          severity: 'high' as const,
        },
        {
          timestamp: '2024-01-02T00:00:00Z',
          eventType: SecurityEventType.USER_ACCESS,
          containerId: 'container2',
          userId: 'user2',
          action: 'action2',
          details: {},
          severity: 'medium' as const,
        },
      ];

      mockReadFile.mockResolvedValue(mockLogs.map(log => JSON.stringify(log)).join('\n'));

      const logs = await auditLogger.getAuditLogs({
        startDate: new Date('2024-01-01'),
        endDate: new Date('2024-01-02'),
        eventType: SecurityEventType.POLICY_CHANGE,
        severity: 'high',
        containerId: 'container1',
      });

      expect(logs).toHaveLength(1);
      expect(logs[0]).toEqual(mockLogs[0]);
    });

    it('should handle errors when retrieving logs', async () => {
      const error = new Error('Failed to read logs');
      mockReadFile.mockRejectedValue(error);

      await expect(auditLogger.getAuditLogs()).rejects.toThrow(error);
      expect(mockLogger.error).toHaveBeenCalledWith(
        'Failed to retrieve audit logs',
        error
      );
    });
  });

  describe('rotateLogs', () => {
    it('should rotate logs when size limit is reached', async () => {
      mockStat.mockResolvedValue({ size: 11 * 1024 * 1024 } as any);
      mockWriteFile.mockResolvedValue(undefined);

      await auditLogger.rotateLogs();

      expect(mockWriteFile).toHaveBeenCalledWith(
        expect.stringContaining('security-audit.log'),
        ''
      );
    });

    it('should handle errors during log rotation', async () => {
      const error = new Error('Failed to rotate logs');
      mockStat.mockResolvedValue({ size: 11 * 1024 * 1024 } as any);
      mockWriteFile.mockRejectedValue(error);

      await expect(auditLogger.rotateLogs()).rejects.toThrow(error);
      expect(mockLogger.error).toHaveBeenCalledWith(
        'Failed to rotate audit logs',
        error
      );
    });
  });
}); 