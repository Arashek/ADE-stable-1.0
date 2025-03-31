export interface FileService {
  saveFile(path: string, content: string): Promise<void>;
  readFile(path: string): Promise<string>;
} 