import { Logger } from '../logging/Logger';
import { writeFile, appendFile } from 'fs/promises';
import { join } from 'path';

export interface SecurityEvent {
  timestamp: string;
  eventType: SecurityEventType;
  containerId: string;
  userId: string;
  action: string;
  details: Record<string, any>;
  severity: 'low' | 'medium' | 'high' | 'critical';
}

export enum SecurityEventType {
  POLICY_CHANGE = 'POLICY_CHANGE',
  USER_ACCESS = 'USER_ACCESS',
  NETWORK_CHANGE = 'NETWORK_CHANGE',
  PERMISSION_CHANGE = 'PERMISSION_CHANGE',
  SECURITY_VIOLATION = 'SECURITY_VIOLATION',
  CONTAINER_START = 'CONTAINER_START',
  CONTAINER_STOP = 'CONTAINER_STOP',
  RESOURCE_LIMIT = 'RESOURCE_LIMIT',
  CAPABILITY_CHANGE = 'CAPABILITY_CHANGE',
}

export class SecurityAuditLogger {
  private logger: Logger;
  private auditLogPath: string;
  private readonly MAX_LOG_SIZE = 10 * 1024 * 1024; // 10MB
  private readonly MAX_LOG_FILES = 5;

  constructor(auditLogPath: string = '/var/log/ade/security') {
    this.logger = new Logger('SecurityAuditLogger');
    this.auditLogPath = auditLogPath;
  }

  async logEvent(event: Omit<SecurityEvent, 'timestamp'>): Promise<void> {
    try {
      const timestamp = new Date().toISOString();
      const fullEvent: SecurityEvent = { ...event, timestamp };
      
      // Format event for logging
      const logEntry = this.formatEvent(fullEvent);
      
      // Write to audit log file
      await this.writeToLogFile(logEntry);
      
      // Log to system logger based on severity
      this.logToSystemLogger(fullEvent);
      
      this.logger.info(`Security event logged: ${event.eventType}`);
    } catch (error) {
      this.logger.error('Failed to log security event', error);
      throw error;
    }
  }

  async getAuditLogs(
    filters: {
      startDate?: Date;
      endDate?: Date;
      eventType?: SecurityEventType;
      severity?: SecurityEvent['severity'];
      containerId?: string;
    } = {}
  ): Promise<SecurityEvent[]> {
    try {
      const logContent = await this.readLogFile();
      const events = this.parseLogContent(logContent);
      
      return events.filter(event => {
        const eventDate = new Date(event.timestamp);
        
        if (filters.startDate && eventDate < filters.startDate) return false;
        if (filters.endDate && eventDate > filters.endDate) return false;
        if (filters.eventType && event.eventType !== filters.eventType) return false;
        if (filters.severity && event.severity !== filters.severity) return false;
        if (filters.containerId && event.containerId !== filters.containerId) return false;
        
        return true;
      });
    } catch (error) {
      this.logger.error('Failed to retrieve audit logs', error);
      throw error;
    }
  }

  async rotateLogs(): Promise<void> {
    try {
      const currentLogPath = join(this.auditLogPath, 'security-audit.log');
      const stats = await this.getLogFileStats(currentLogPath);
      
      if (stats.size >= this.MAX_LOG_SIZE) {
        // Rotate existing log files
        for (let i = this.MAX_LOG_FILES - 1; i > 0; i--) {
          const oldPath = join(this.auditLogPath, `security-audit.${i}.log`);
          const newPath = join(this.auditLogPath, `security-audit.${i + 1}.log`);
          await this.rotateLogFile(oldPath, newPath);
        }
        
        // Move current log to .1
        await this.rotateLogFile(currentLogPath, join(this.auditLogPath, 'security-audit.1.log'));
        
        // Create new empty log file
        await writeFile(currentLogPath, '');
      }
    } catch (error) {
      this.logger.error('Failed to rotate audit logs', error);
      throw error;
    }
  }

  private async writeToLogFile(logEntry: string): Promise<void> {
    const logPath = join(this.auditLogPath, 'security-audit.log');
    await appendFile(logPath, logEntry + '\n');
    await this.rotateLogs();
  }

  private async readLogFile(): Promise<string> {
    const logPath = join(this.auditLogPath, 'security-audit.log');
    return await appendFile(logPath, '');
  }

  private async getLogFileStats(logPath: string): Promise<{ size: number }> {
    const { stat } = await import('fs/promises');
    return await stat(logPath);
  }

  private async rotateLogFile(oldPath: string, newPath: string): Promise<void> {
    const { rename } = await import('fs/promises');
    try {
      await rename(oldPath, newPath);
    } catch (error) {
      if ((error as NodeJS.ErrnoException).code !== 'ENOENT') {
        throw error;
      }
    }
  }

  private formatEvent(event: SecurityEvent): string {
    return JSON.stringify({
      timestamp: event.timestamp,
      eventType: event.eventType,
      containerId: event.containerId,
      userId: event.userId,
      action: event.action,
      details: event.details,
      severity: event.severity,
    });
  }

  private parseLogContent(content: string): SecurityEvent[] {
    return content
      .split('\n')
      .filter(line => line.trim())
      .map(line => JSON.parse(line));
  }

  private logToSystemLogger(event: SecurityEvent): void {
    const message = `Security Event: ${event.eventType} - ${event.action} (Severity: ${event.severity})`;
    
    switch (event.severity) {
      case 'critical':
        this.logger.error(message);
        break;
      case 'high':
        this.logger.warn(message);
        break;
      case 'medium':
        this.logger.info(message);
        break;
      case 'low':
        this.logger.debug(message);
        break;
    }
  }
} 