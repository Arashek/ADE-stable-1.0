import { PerformanceMonitor } from '../monitoring/PerformanceMonitor';
import { RefactoringService } from '../refactoring/RefactoringService';

export interface DocumentationOptions {
  includePerformanceMetrics: boolean;
  includeRefactoringHistory: boolean;
  includeCodeExamples: boolean;
  format: 'markdown' | 'html' | 'pdf';
}

export interface GeneratedDocumentation {
  content: string;
  metadata: {
    generatedAt: Date;
    version: string;
    components: string[];
  };
}

export class DocumentationGenerator {
  private static instance: DocumentationGenerator;
  private performanceMonitor: PerformanceMonitor;
  private refactoringService: RefactoringService;

  private constructor() {
    this.performanceMonitor = PerformanceMonitor.getInstance();
    this.refactoringService = RefactoringService.getInstance();
  }

  public static getInstance(): DocumentationGenerator {
    if (!DocumentationGenerator.instance) {
      DocumentationGenerator.instance = new DocumentationGenerator();
    }
    return DocumentationGenerator.instance;
  }

  public async generateDocumentation(options: DocumentationOptions): Promise<GeneratedDocumentation> {
    const sections: string[] = [];

    // Generate component documentation
    sections.push(await this.generateComponentDocumentation());

    // Generate API documentation
    sections.push(await this.generateAPIDocumentation());

    // Generate performance metrics if requested
    if (options.includePerformanceMetrics) {
      sections.push(await this.generatePerformanceDocumentation());
    }

    // Generate refactoring history if requested
    if (options.includeRefactoringHistory) {
      sections.push(await this.generateRefactoringDocumentation());
    }

    // Generate code examples if requested
    if (options.includeCodeExamples) {
      sections.push(await this.generateCodeExamples());
    }

    // Format the content based on the requested format
    const content = this.formatContent(sections.join('\n\n'), options.format);

    return {
      content,
      metadata: {
        generatedAt: new Date(),
        version: '1.0.0', // This should come from package.json
        components: ['editor', 'refactoring', 'debugging', 'security']
      }
    };
  }

  private async generateComponentDocumentation(): Promise<string> {
    return `
# Component Documentation

## Code Editor
The code editor component provides a rich editing experience with features like:
- Syntax highlighting
- Code completion
- Error detection
- Refactoring support
- Debugging capabilities

## Refactoring Panel
The refactoring panel enables code transformations with:
- Extract method
- Rename symbol
- Extract variable
- Inline variable
- Move method
- Change signature

## Debugger Panel
The debugger panel offers comprehensive debugging features:
- Breakpoint management
- Variable inspection
- Call stack viewing
- Expression evaluation
- Step-by-step execution

## Security Analysis Panel
The security analysis panel provides:
- Vulnerability scanning
- Compliance checking
- Issue tracking
- Fix suggestions
- Security best practices
    `;
  }

  private async generateAPIDocumentation(): Promise<string> {
    return `
# API Documentation

## Editor API
\`\`\`typescript
interface EditorAPI {
  getContent(): string;
  setContent(content: string): void;
  getSelection(): Selection;
  setSelection(selection: Selection): void;
  focus(): void;
  blur(): void;
}
\`\`\`

## Refactoring API
\`\`\`typescript
interface RefactoringAPI {
  applyRefactoring(operation: RefactoringOperation): Promise<void>;
  previewRefactoring(operation: RefactoringOperation): Promise<string>;
  undo(): void;
  redo(): void;
}
\`\`\`

## Debugging API
\`\`\`typescript
interface DebuggingAPI {
  addBreakpoint(line: number): void;
  removeBreakpoint(line: number): void;
  stepOver(): void;
  stepInto(): void;
  continue(): void;
  evaluateExpression(expression: string): Promise<any>;
}
\`\`\`
    `;
  }

  private async generatePerformanceDocumentation(): Promise<string> {
    const performanceReport = this.performanceMonitor.generateReport();
    
    return `
# Performance Metrics

## Editor Operations
- Average response time: ${performanceReport.summary.average.toFixed(2)}ms
- 95th percentile: ${performanceReport.summary.p95.toFixed(2)}ms
- 99th percentile: ${performanceReport.summary.p99.toFixed(2)}ms

## Recent Metrics
${performanceReport.metrics.slice(-5).map(m => `- ${m.name}: ${m.value}ms`).join('\n')}
    `;
  }

  private async generateRefactoringDocumentation(): Promise<string> {
    const history = this.refactoringService.getHistory();
    
    return `
# Refactoring History

## Recent Operations
${history.slice(-5).map(op => `
### ${op.type}
- File: ${op.file}
- Line: ${op.line}
- Status: ${op.status}
- Description: ${op.description}
`).join('\n')}
    `;
  }

  private async generateCodeExamples(): Promise<string> {
    return `
# Code Examples

## Editor Usage
\`\`\`typescript
// Initialize editor
const editor = new CodeEditor({
  content: initialContent,
  language: 'typescript'
});

// Handle content changes
editor.onContentChange((content) => {
  console.log('Content updated:', content);
});

// Apply formatting
editor.formatDocument();
\`\`\`

## Refactoring Usage
\`\`\`typescript
// Extract method
const operation = {
  type: 'extract-method',
  description: 'Extract complex calculation',
  file: 'calculator.ts',
  line: 42
};

await refactoringService.applyRefactoring(operation);
\`\`\`

## Debugging Usage
\`\`\`typescript
// Add breakpoint
debugger.addBreakpoint(42);

// Evaluate expression
const result = await debugger.evaluateExpression('x + y');

// Step through code
debugger.stepOver();
\`\`\`
    `;
  }

  private formatContent(content: string, format: DocumentationOptions['format']): string {
    switch (format) {
      case 'html':
        return this.convertToHTML(content);
      case 'pdf':
        return this.convertToPDF(content);
      default:
        return content;
    }
  }

  private convertToHTML(content: string): string {
    // Convert markdown to HTML
    return `
<!DOCTYPE html>
<html>
<head>
  <title>ADE Platform Documentation</title>
  <style>
    body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; }
    pre { background: #f5f5f5; padding: 1em; border-radius: 4px; }
    code { font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace; }
  </style>
</head>
<body>
  ${content}
</body>
</html>
    `;
  }

  private convertToPDF(content: string): string {
    // This would typically use a PDF generation library
    // For now, we'll just return the content
    return content;
  }
} 