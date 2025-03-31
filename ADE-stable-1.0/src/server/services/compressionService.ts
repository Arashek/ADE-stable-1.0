import zlib from 'zlib';
import { promisify } from 'util';

const gzip = promisify(zlib.gzip);
const gunzip = promisify(zlib.gunzip);

class CompressionService {
  private readonly compressionThreshold = 1024; // Compress messages larger than 1KB

  public async shouldCompress(data: string): Promise<boolean> {
    return Buffer.byteLength(data) > this.compressionThreshold;
  }

  public async compress(data: string): Promise<Buffer> {
    try {
      return await gzip(Buffer.from(data));
    } catch (error) {
      console.error('Compression failed:', error);
      throw error;
    }
  }

  public async decompress(data: Buffer): Promise<string> {
    try {
      const decompressed = await gunzip(data);
      return decompressed.toString();
    } catch (error) {
      console.error('Decompression failed:', error);
      throw error;
    }
  }
}

export const compressionService = new CompressionService(); 