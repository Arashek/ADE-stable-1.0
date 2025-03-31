import { Buffer } from 'buffer';
import { createHmac } from 'crypto-browserify';
import { performanceMonitor } from './performance';

interface SignedRequest extends Request {
  headers: Headers & {
    get(name: string): string | null;
    set(name: string, value: string): void;
  };
}

export class SecurityService {
  private readonly apiKey: string;
  private readonly apiSecret: string;

  constructor(apiKey: string, apiSecret: string) {
    this.apiKey = apiKey;
    this.apiSecret = apiSecret;
  }

  /**
   * Signs a request with a timestamp and HMAC signature
   */
  public signRequest(request: Request): SignedRequest {
    const startTime = performance.now();
    const timestamp = Date.now().toString();
    const signedRequest = request.clone() as SignedRequest;
    const signature = this.generateSignature(request, timestamp);

    signedRequest.headers.set('X-API-Key', this.apiKey);
    signedRequest.headers.set('X-Timestamp', timestamp);
    signedRequest.headers.set('X-Signature', signature);

    const duration = performance.now() - startTime;
    performanceMonitor.recordMetric('request-signing', duration);

    return signedRequest;
  }

  /**
   * Generates an HMAC signature for the request
   */
  private generateSignature(request: Request, timestamp: string): string {
    const startTime = performance.now();
    const method = request.method.toUpperCase();
    const url = new URL(request.url);
    const path = url.pathname + url.search;

    // Create string to sign
    const stringToSign = [
      method,
      path,
      timestamp,
      this.apiKey
    ].join('\n');

    // Generate HMAC signature
    const hmac = createHmac('sha256', this.apiSecret);
    hmac.update(stringToSign);
    const signature = hmac.digest('base64');

    const duration = performance.now() - startTime;
    performanceMonitor.recordMetric('signature-generation', duration);

    return signature;
  }

  /**
   * Validates a response signature
   */
  public validateResponse(response: Response, signature: string): boolean {
    const startTime = performance.now();
    
    if (!signature) {
      performanceMonitor.recordMetric('signature-validation-failed', 1);
      return false;
    }

    const timestamp = response.headers.get('X-Timestamp');
    if (!timestamp) {
      performanceMonitor.recordMetric('signature-validation-failed', 1);
      return false;
    }

    const calculatedSignature = this.generateResponseSignature(response, timestamp);
    const isValid = signature === calculatedSignature;
    
    const duration = performance.now() - startTime;
    performanceMonitor.recordMetric('signature-validation', duration);
    
    if (!isValid) {
      performanceMonitor.recordMetric('signature-validation-failed', 1);
    }

    return isValid;
  }

  /**
   * Generates a signature for response validation
   */
  private generateResponseSignature(response: Response, timestamp: string): string {
    const startTime = performance.now();
    
    const stringToSign = [
      response.status,
      response.headers.get('Content-Type'),
      timestamp,
      this.apiKey
    ].join('\n');

    const hmac = createHmac('sha256', this.apiSecret);
    hmac.update(stringToSign);
    const signature = hmac.digest('base64');

    const duration = performance.now() - startTime;
    performanceMonitor.recordMetric('response-signature-generation', duration);

    return signature;
  }
}

/**
 * Creates a secure fetch wrapper with request signing
 */
export const createSecureFetch = (apiKey: string, apiSecret: string) => {
  const security = new SecurityService(apiKey, apiSecret);

  return async (input: RequestInfo, init?: RequestInit): Promise<Response> => {
    const startTime = performance.now();
    const request = new Request(input, init);
    const signedRequest = security.signRequest(request);

    try {
      const response = await fetch(signedRequest);
      const signature = response.headers.get('X-Signature');

      if (signature && !security.validateResponse(response, signature)) {
        performanceMonitor.recordMetric('secure-fetch-error', 1);
        throw new Error('Invalid response signature');
      }

      const duration = performance.now() - startTime;
      performanceMonitor.recordMetric('secure-fetch', duration);

      return response;
    } catch (error) {
      performanceMonitor.recordMetric('secure-fetch-error', 1);
      throw error;
    }
  };
}; 