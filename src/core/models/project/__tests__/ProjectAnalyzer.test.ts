import { ProjectAnalyzer } from '../ProjectAnalyzer';
import * as fs from 'fs';
import * as path from 'path';

jest.mock('fs');
jest.mock('path');

describe('ProjectAnalyzer', () => {
  let analyzer: ProjectAnalyzer;
  const mockProjectRoot = '/mock/project/root';

  beforeEach(() => {
    analyzer = new ProjectAnalyzer(mockProjectRoot);
    jest.clearAllMocks();
  });

  describe('analyze', () => {
    it('should analyze a JavaScript project', async () => {
      const mockFiles = ['package.json', 'src/index.js'];
      const mockPackageJson = {
        dependencies: {
          react: '^18.2.0',
          next: '^13.0.0'
        },
        devDependencies: {
          typescript: '^4.9.0'
        },
        scripts: {
          start: 'next start',
          dev: 'next dev',
          test: 'jest'
        }
      };

      (fs.promises.readdir as jest.Mock).mockResolvedValue(mockFiles);
      (fs.promises.readFile as jest.Mock).mockResolvedValue(JSON.stringify(mockPackageJson));

      const result = await analyzer.analyze();

      expect(result.language).toBe('javascript');
      expect(result.framework).toBe('next');
      expect(result.buildTool).toBe('next');
      expect(result.dependencies).toHaveLength(2);
      expect(result.devDependencies).toHaveLength(1);
      expect(result.scripts).toEqual(mockPackageJson.scripts);
    });

    it('should analyze a Python project', async () => {
      const mockFiles = ['requirements.txt', 'app.py'];
      const mockRequirements = 'flask==2.0.1\ndjango==3.2.0';

      (fs.promises.readdir as jest.Mock).mockResolvedValue(mockFiles);
      (fs.promises.readFile as jest.Mock).mockResolvedValue(mockRequirements);

      const result = await analyzer.analyze();

      expect(result.language).toBe('python');
      expect(result.framework).toBe('flask');
      expect(result.buildTool).toBe('setuptools');
    });

    it('should detect ports from code files', async () => {
      const mockFiles = ['package.json', 'src/server.js'];
      const mockServerContent = 'const port = 3000;';
      const mockPackageJson = {
        dependencies: {
          express: '^4.17.1'
        }
      };

      (fs.promises.readdir as jest.Mock).mockResolvedValue(mockFiles);
      (fs.promises.readFile as jest.Mock)
        .mockResolvedValueOnce(JSON.stringify(mockPackageJson))
        .mockResolvedValueOnce(mockServerContent);

      const result = await analyzer.analyze();

      expect(result.ports).toContain(3000);
    });

    it('should detect environment variables from .env files', async () => {
      const mockFiles = ['package.json', '.env'];
      const mockEnvContent = 'API_KEY=123\nDB_URL=mongodb://localhost';
      const mockPackageJson = {
        dependencies: {}
      };

      (fs.promises.readdir as jest.Mock).mockResolvedValue(mockFiles);
      (fs.promises.readFile as jest.Mock)
        .mockResolvedValueOnce(JSON.stringify(mockPackageJson))
        .mockResolvedValueOnce(mockEnvContent);

      const result = await analyzer.analyze();

      expect(result.environment).toEqual({
        API_KEY: '123',
        DB_URL: 'mongodb://localhost'
      });
    });

    it('should throw error for unsupported project type', async () => {
      const mockFiles = ['unknown.file'];

      (fs.promises.readdir as jest.Mock).mockResolvedValue(mockFiles);

      await expect(analyzer.analyze()).rejects.toThrow('Could not detect project language');
    });
  });
}); 