import { Redis } from 'ioredis';
import { S3 } from 'aws-sdk';
import { Storage } from '@google-cloud/storage';
import { SecretManagerServiceClient } from '@google-cloud/secret-manager';
import { encrypt, decrypt } from '../security/encryption';
import { CloudConfig, CloudProvider, CloudCredentials } from '../types/cloud.types';
import { CloudMetrics } from '../types/metrics.types';

interface CloudServiceConfig {
  redisUrl: string;
  defaultProvider: CloudProvider;
  encryptionKey: string;
  metricsEnabled: boolean;
}

export class CloudIntegrationService {
  private redis: Redis;
  private s3Client?: S3;
  private gcsClient?: Storage;
  private secretManager?: SecretManagerServiceClient;
  private config: CloudServiceConfig;
  private metrics: CloudMetrics = {
    requests: 0,
    errors: 0,
    latency: 0,
    lastUpdated: Date.now()
  };

  constructor(config: CloudServiceConfig) {
    this.redis = new Redis(config.redisUrl);
    this.config = config;
  }

  public async initialize(credentials: CloudCredentials): Promise<void> {
    // Initialize cloud clients based on provider
    switch (this.config.defaultProvider) {
      case 'aws':
        await this.initializeAWS(credentials.aws);
        break;
      case 'gcp':
        await this.initializeGCP(credentials.gcp);
        break;
      default:
        throw new Error('Unsupported cloud provider');
    }

    // Store encrypted credentials
    await this.storeCredentials(credentials);
  }

  private async initializeAWS(awsConfig: any): Promise<void> {
    this.s3Client = new S3({
      region: awsConfig.region,
      credentials: {
        accessKeyId: awsConfig.accessKeyId,
        secretAccessKey: awsConfig.secretAccessKey
      }
    });

    // Test connection
    await this.s3Client.listBuckets().promise();
  }

  private async initializeGCP(gcpConfig: any): Promise<void> {
    this.gcsClient = new Storage({
      projectId: gcpConfig.projectId,
      credentials: gcpConfig.credentials
    });

    this.secretManager = new SecretManagerServiceClient({
      projectId: gcpConfig.projectId,
      credentials: gcpConfig.credentials
    });

    // Test connection
    await this.gcsClient.getBuckets();
  }

  private async storeCredentials(credentials: CloudCredentials): Promise<void> {
    const encryptedCredentials = encrypt(
      JSON.stringify(credentials),
      this.config.encryptionKey
    );

    await this.redis.set(
      'cloud_credentials',
      encryptedCredentials,
      'EX',
      3600 // 1 hour expiry
    );
  }

  public async uploadFile(
    file: Buffer,
    path: string,
    options: {
      provider?: CloudProvider;
      bucket?: string;
      metadata?: Record<string, string>;
      encryption?: boolean;
    } = {}
  ): Promise<string> {
    const startTime = Date.now();
    try {
      const provider = options.provider || this.config.defaultProvider;
      const bucket = options.bucket || await this.getDefaultBucket(provider);

      let processedFile = file;
      if (options.encryption) {
        processedFile = encrypt(file, this.config.encryptionKey);
      }

      let url: string;
      switch (provider) {
        case 'aws':
          url = await this.uploadToS3(processedFile, path, bucket, options.metadata);
          break;
        case 'gcp':
          url = await this.uploadToGCS(processedFile, path, bucket, options.metadata);
          break;
        default:
          throw new Error('Unsupported cloud provider');
      }

      this.updateMetrics(Date.now() - startTime);
      return url;
    } catch (error) {
      this.updateMetrics(Date.now() - startTime, true);
      throw error;
    }
  }

  private async uploadToS3(
    file: Buffer,
    path: string,
    bucket: string,
    metadata?: Record<string, string>
  ): Promise<string> {
    if (!this.s3Client) throw new Error('AWS S3 client not initialized');

    const params = {
      Bucket: bucket,
      Key: path,
      Body: file,
      Metadata: metadata,
      ServerSideEncryption: 'AES256'
    };

    const result = await this.s3Client.upload(params).promise();
    return result.Location;
  }

  private async uploadToGCS(
    file: Buffer,
    path: string,
    bucket: string,
    metadata?: Record<string, string>
  ): Promise<string> {
    if (!this.gcsClient) throw new Error('GCS client not initialized');

    const bucketClient = this.gcsClient.bucket(bucket);
    const blob = bucketClient.file(path);
    
    await blob.save(file, {
      metadata: {
        ...metadata,
        encryption: 'AES256'
      }
    });

    return `https://storage.googleapis.com/${bucket}/${path}`;
  }

  public async downloadFile(
    path: string,
    options: {
      provider?: CloudProvider;
      bucket?: string;
      decryption?: boolean;
    } = {}
  ): Promise<Buffer> {
    const startTime = Date.now();
    try {
      const provider = options.provider || this.config.defaultProvider;
      const bucket = options.bucket || await this.getDefaultBucket(provider);

      let file: Buffer;
      switch (provider) {
        case 'aws':
          file = await this.downloadFromS3(path, bucket);
          break;
        case 'gcp':
          file = await this.downloadFromGCS(path, bucket);
          break;
        default:
          throw new Error('Unsupported cloud provider');
      }

      if (options.decryption) {
        file = decrypt(file, this.config.encryptionKey);
      }

      this.updateMetrics(Date.now() - startTime);
      return file;
    } catch (error) {
      this.updateMetrics(Date.now() - startTime, true);
      throw error;
    }
  }

  private async downloadFromS3(path: string, bucket: string): Promise<Buffer> {
    if (!this.s3Client) throw new Error('AWS S3 client not initialized');

    const params = {
      Bucket: bucket,
      Key: path
    };

    const result = await this.s3Client.getObject(params).promise();
    return result.Body as Buffer;
  }

  private async downloadFromGCS(path: string, bucket: string): Promise<Buffer> {
    if (!this.gcsClient) throw new Error('GCS client not initialized');

    const bucketClient = this.gcsClient.bucket(bucket);
    const blob = bucketClient.file(path);
    
    const [file] = await blob.download();
    return file;
  }

  public async getSecret(
    secretName: string,
    options: {
      provider?: CloudProvider;
      version?: string;
    } = {}
  ): Promise<string> {
    const provider = options.provider || this.config.defaultProvider;
    
    switch (provider) {
      case 'aws':
        return this.getSecretFromAWS(secretName, options.version);
      case 'gcp':
        return this.getSecretFromGCP(secretName, options.version);
      default:
        throw new Error('Unsupported cloud provider');
    }
  }

  private async getSecretFromAWS(secretName: string, version?: string): Promise<string> {
    // Implementation for AWS Secrets Manager
    throw new Error('Not implemented');
  }

  private async getSecretFromGCP(secretName: string, version?: string): Promise<string> {
    if (!this.secretManager) throw new Error('GCP Secret Manager not initialized');

    const [version] = await this.secretManager.accessSecretVersion({
      name: `${secretName}/versions/${version || 'latest'}`
    });

    return version.payload?.data?.toString() || '';
  }

  private async getDefaultBucket(provider: CloudProvider): Promise<string> {
    const bucket = await this.redis.get(`cloud_bucket_${provider}`);
    if (!bucket) {
      throw new Error(`No default bucket configured for provider: ${provider}`);
    }
    return bucket;
  }

  private updateMetrics(latency: number, isError: boolean = false): void {
    if (!this.config.metricsEnabled) return;

    this.metrics.requests++;
    if (isError) this.metrics.errors++;
    this.metrics.latency = (this.metrics.latency + latency) / 2;
    this.metrics.lastUpdated = Date.now();

    // Store metrics in Redis
    this.redis.set('cloud_metrics', JSON.stringify(this.metrics));
  }

  public async getMetrics(): Promise<CloudMetrics> {
    if (!this.config.metricsEnabled) {
      throw new Error('Metrics collection is disabled');
    }
    return this.metrics;
  }

  public async rotateCredentials(): Promise<void> {
    const encryptedCredentials = await this.redis.get('cloud_credentials');
    if (!encryptedCredentials) {
      throw new Error('No credentials found to rotate');
    }

    const credentials = JSON.parse(
      decrypt(encryptedCredentials, this.config.encryptionKey)
    );

    // Implement credential rotation logic here
    // This would typically involve:
    // 1. Creating new credentials
    // 2. Updating the credentials in the cloud provider
    // 3. Storing the new credentials
    // 4. Updating any active connections

    throw new Error('Credential rotation not implemented');
  }

  public async validateConnection(provider?: CloudProvider): Promise<boolean> {
    const targetProvider = provider || this.config.defaultProvider;
    
    try {
      switch (targetProvider) {
        case 'aws':
          await this.s3Client?.listBuckets().promise();
          break;
        case 'gcp':
          await this.gcsClient?.getBuckets();
          break;
        default:
          throw new Error('Unsupported cloud provider');
      }
      return true;
    } catch (error) {
      console.error(`Failed to validate connection to ${targetProvider}:`, error);
      return false;
    }
  }
} 