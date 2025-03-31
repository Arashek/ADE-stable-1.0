export type LogLevel = 'debug' | 'info' | 'warn' | 'error';

export interface LogEntry {
  timestamp: Date;
  level: LogLevel;
  message: string;
  context?: Record<string, any>;
  error?: Error;
}

export interface LogTransport {
  log(entry: LogEntry): void;
}

export class ConsoleTransport implements LogTransport {
  log(entry: LogEntry): void {
    const { timestamp, level, message, context, error } = entry;
    const timestampStr = timestamp.toISOString();
    const contextStr = context ? JSON.stringify(context) : '';
    const errorStr = error ? `\nError: ${error.message}\nStack: ${error.stack}` : '';

    const logMessage = `[${timestampStr}] ${level.toUpperCase()}: ${message} ${contextStr}${errorStr}`;

    switch (level) {
      case 'debug':
        console.debug(logMessage);
        break;
      case 'info':
        console.info(logMessage);
        break;
      case 'warn':
        console.warn(logMessage);
        break;
      case 'error':
        console.error(logMessage);
        break;
    }
  }
}

export class FileTransport implements LogTransport {
  private fileHandle: any; // In a real implementation, this would be a file handle

  constructor(private filePath: string) {
    // In a real implementation, this would open the file
  }

  log(entry: LogEntry): void {
    const { timestamp, level, message, context, error } = entry;
    const timestampStr = timestamp.toISOString();
    const contextStr = context ? JSON.stringify(context) : '';
    const errorStr = error ? `\nError: ${error.message}\nStack: ${error.stack}` : '';

    const logMessage = `[${timestampStr}] ${level.toUpperCase()}: ${message} ${contextStr}${errorStr}\n`;

    // In a real implementation, this would write to the file
    console.log(`Writing to file ${this.filePath}: ${logMessage}`);
  }

  close(): void {
    // In a real implementation, this would close the file handle
  }
}

export class Logger {
  private transports: LogTransport[];
  private minLevel: LogLevel;

  constructor(
    private name: string,
    options: {
      minLevel?: LogLevel;
      transports?: LogTransport[];
    } = {}
  ) {
    this.minLevel = options.minLevel || 'info';
    this.transports = options.transports || [new ConsoleTransport()];
  }

  public debug(message: string, context?: Record<string, any>): void {
    this.log('debug', message, context);
  }

  public info(message: string, context?: Record<string, any>): void {
    this.log('info', message, context);
  }

  public warn(message: string, context?: Record<string, any>): void {
    this.log('warn', message, context);
  }

  public error(message: string, error?: Error, context?: Record<string, any>): void {
    this.log('error', message, context, error);
  }

  private log(level: LogLevel, message: string, context?: Record<string, any>, error?: Error): void {
    if (!this.shouldLog(level)) return;

    const entry: LogEntry = {
      timestamp: new Date(),
      level,
      message,
      context: {
        ...context,
        logger: this.name
      },
      error
    };

    for (const transport of this.transports) {
      transport.log(entry);
    }
  }

  private shouldLog(level: LogLevel): boolean {
    const levels: LogLevel[] = ['debug', 'info', 'warn', 'error'];
    return levels.indexOf(level) >= levels.indexOf(this.minLevel);
  }

  public addTransport(transport: LogTransport): void {
    this.transports.push(transport);
  }

  public setMinLevel(level: LogLevel): void {
    this.minLevel = level;
  }
} 