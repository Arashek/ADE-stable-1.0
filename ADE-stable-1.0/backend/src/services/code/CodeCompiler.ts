import { CodeImplementation } from '../../../frontend/src/services/CodeImplementationService';
import * as fs from 'fs';
import * as path from 'path';
import { exec } from 'child_process';
import { promisify } from 'util';

const execAsync = promisify(exec);

export class CodeCompiler {
  private readonly buildDir: string;
  private readonly tempDir: string;

  constructor() {
    this.buildDir = path.join(process.cwd(), 'build');
    this.tempDir = path.join(process.cwd(), 'temp');
    this.ensureDirectories();
  }

  private ensureDirectories() {
    if (!fs.existsSync(this.buildDir)) {
      fs.mkdirSync(this.buildDir, { recursive: true });
    }
    if (!fs.existsSync(this.tempDir)) {
      fs.mkdirSync(this.tempDir, { recursive: true });
    }
  }

  public async compileImplementation(implementation: CodeImplementation): Promise<{
    success: boolean;
    output?: string;
    error?: string;
  }> {
    try {
      // Create temporary project directory
      const projectDir = path.join(this.tempDir, implementation.id);
      if (fs.existsSync(projectDir)) {
        fs.rmSync(projectDir, { recursive: true, force: true });
      }
      fs.mkdirSync(projectDir, { recursive: true });

      // Write files
      for (const file of implementation.files) {
        const filePath = path.join(projectDir, file.path);
        const dirPath = path.dirname(filePath);
        if (!fs.existsSync(dirPath)) {
          fs.mkdirSync(dirPath, { recursive: true });
        }
        fs.writeFileSync(filePath, file.content);
      }

      // Create package.json if needed
      if (!fs.existsSync(path.join(projectDir, 'package.json'))) {
        await this.createPackageJson(projectDir, implementation);
      }

      // Install dependencies
      await this.installDependencies(projectDir);

      // Run build process
      const buildResult = await this.runBuildProcess(projectDir);

      if (buildResult.success) {
        // Copy build output to build directory
        const buildOutputDir = path.join(this.buildDir, implementation.id);
        if (fs.existsSync(buildOutputDir)) {
          fs.rmSync(buildOutputDir, { recursive: true, force: true });
        }
        fs.mkdirSync(buildOutputDir, { recursive: true });

        // Copy build files
        const buildDir = path.join(projectDir, 'dist');
        if (fs.existsSync(buildDir)) {
          this.copyDirectory(buildDir, buildOutputDir);
        }

        return {
          success: true,
          output: buildResult.output,
        };
      } else {
        return {
          success: false,
          error: buildResult.error,
        };
      }
    } catch (error) {
      return {
        success: false,
        error: error.message,
      };
    }
  }

  private async createPackageJson(projectDir: string, implementation: CodeImplementation) {
    const packageJson = {
      name: implementation.name.toLowerCase().replace(/\s+/g, '-'),
      version: '1.0.0',
      description: implementation.description,
      main: 'index.js',
      scripts: {
        build: 'tsc && webpack --mode production',
        test: 'jest',
        start: 'node dist/index.js',
      },
      dependencies: this.extractDependencies(implementation),
      devDependencies: {
        typescript: '^4.9.5',
        webpack: '^5.75.0',
        webpack-cli: '^5.0.1',
        ts-loader: '^9.4.2',
        '@types/node': '^18.11.18',
        jest: '^29.3.1',
        '@types/jest': '^29.2.5',
        'ts-jest': '^29.0.5'
      },
    };

    fs.writeFileSync(
      path.join(projectDir, 'package.json'),
      JSON.stringify(packageJson, null, 2)
    );
  }

  private extractDependencies(implementation: CodeImplementation): Record<string, string> {
    const dependencies: Record<string, string> = {};

    // Extract dependencies from import statements
    for (const file of implementation.files) {
      const importRegex = /import\s+.*\s+from\s+['"]([^'"]+)['"]/g;
      let match;
      while ((match = importRegex.exec(file.content)) !== null) {
        const packageName = match[1].split('/')[0];
        if (!dependencies[packageName]) {
          dependencies[packageName] = 'latest';
        }
      }
    }

    return dependencies;
  }

  private async installDependencies(projectDir: string) {
    try {
      await execAsync('npm install', { cwd: projectDir });
    } catch (error) {
      throw new Error(`Failed to install dependencies: ${error.message}`);
    }
  }

  private async runBuildProcess(projectDir: string): Promise<{
    success: boolean;
    output?: string;
    error?: string;
  }> {
    try {
      const { stdout, stderr } = await execAsync('npm run build', { cwd: projectDir });
      return {
        success: true,
        output: stdout,
      };
    } catch (error) {
      return {
        success: false,
        error: error.message,
      };
    }
  }

  private copyDirectory(src: string, dest: string) {
    if (!fs.existsSync(dest)) {
      fs.mkdirSync(dest, { recursive: true });
    }

    const entries = fs.readdirSync(src, { withFileTypes: true });

    for (const entry of entries) {
      const srcPath = path.join(src, entry.name);
      const destPath = path.join(dest, entry.name);

      if (entry.isDirectory()) {
        this.copyDirectory(srcPath, destPath);
      } else {
        fs.copyFileSync(srcPath, destPath);
      }
    }
  }
} 