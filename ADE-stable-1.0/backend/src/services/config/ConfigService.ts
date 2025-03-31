import { injectable } from 'tsyringe';
import dotenv from 'dotenv';

@injectable()
export class ConfigService {
  private config: { [key: string]: string };

  constructor() {
    dotenv.config();
    this.config = process.env as { [key: string]: string };
  }

  public get(key: string): string {
    const value = this.config[key];
    if (value === undefined) {
      throw new Error(`Configuration key ${key} not found`);
    }
    return value;
  }

  public getOptional(key: string): string | undefined {
    return this.config[key];
  }

  public getNumber(key: string): number {
    const value = this.get(key);
    const num = Number(value);
    if (isNaN(num)) {
      throw new Error(`Configuration key ${key} is not a valid number`);
    }
    return num;
  }

  public getBoolean(key: string): boolean {
    const value = this.get(key).toLowerCase();
    if (value !== 'true' && value !== 'false') {
      throw new Error(`Configuration key ${key} is not a valid boolean`);
    }
    return value === 'true';
  }

  public getArray(key: string): string[] {
    const value = this.get(key);
    return value.split(',').map(item => item.trim());
  }

  public set(key: string, value: string): void {
    this.config[key] = value;
    process.env[key] = value;
  }

  public has(key: string): boolean {
    return key in this.config;
  }

  public getAll(): { [key: string]: string } {
    return { ...this.config };
  }
} 