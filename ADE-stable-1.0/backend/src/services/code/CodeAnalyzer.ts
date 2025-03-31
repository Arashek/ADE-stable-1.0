import { CodeFile } from '../../../frontend/src/services/CodeImplementationService';
import * as esprima from 'esprima';
import * as estraverse from 'estraverse';
import * as escodegen from 'escodegen';

export class CodeAnalyzer {
  private readonly complexityThreshold = 10;
  private readonly maintainabilityThreshold = 65;

  public async analyzeFile(file: CodeFile): Promise<{
    complexity: number;
    maintainability: number;
    testCoverage: number;
    issues: Array<{
      type: 'error' | 'warning' | 'info';
      message: string;
      line: number;
      column: number;
    }>;
  }> {
    const issues: Array<{
      type: 'error' | 'warning' | 'info';
      message: string;
      line: number;
      column: number;
    }> = [];

    try {
      // Parse code
      const ast = esprima.parseScript(file.content, {
        loc: true,
        range: true,
        comment: true,
      });

      // Calculate complexity
      const complexity = this.calculateComplexity(ast);
      if (complexity > this.complexityThreshold) {
        issues.push({
          type: 'warning',
          message: `High cyclomatic complexity (${complexity}). Consider refactoring to improve maintainability.`,
          line: 1,
          column: 1,
        });
      }

      // Calculate maintainability
      const maintainability = this.calculateMaintainability(ast);
      if (maintainability < this.maintainabilityThreshold) {
        issues.push({
          type: 'warning',
          message: `Low maintainability score (${maintainability}). Consider improving code organization and documentation.`,
          line: 1,
          column: 1,
        });
      }

      // Analyze code patterns
      this.analyzeCodePatterns(ast, issues);

      // Calculate test coverage (mock for now)
      const testCoverage = await this.calculateTestCoverage(file);

      return {
        complexity,
        maintainability,
        testCoverage,
        issues,
      };
    } catch (error) {
      issues.push({
        type: 'error',
        message: `Failed to analyze code: ${error.message}`,
        line: 1,
        column: 1,
      });

      return {
        complexity: 0,
        maintainability: 0,
        testCoverage: 0,
        issues,
      };
    }
  }

  private calculateComplexity(ast: any): number {
    let complexity = 1; // Base complexity

    estraverse.traverse(ast, {
      enter: (node: any) => {
        // Increase complexity for control structures
        if (
          node.type === 'IfStatement' ||
          node.type === 'SwitchCase' ||
          node.type === 'ForStatement' ||
          node.type === 'WhileStatement' ||
          node.type === 'DoWhileStatement' ||
          node.type === 'CatchClause' ||
          node.type === 'LogicalExpression'
        ) {
          complexity++;
        }
      },
    });

    return complexity;
  }

  private calculateMaintainability(ast: any): number {
    let score = 100;

    // Count lines of code
    const lines = ast.loc.end.line;
    if (lines > 100) {
      score -= 10;
    }

    // Count function declarations
    let functionCount = 0;
    estraverse.traverse(ast, {
      enter: (node: any) => {
        if (node.type === 'FunctionDeclaration' || node.type === 'FunctionExpression') {
          functionCount++;
        }
      },
    });

    if (functionCount > 10) {
      score -= 10;
    }

    // Check for comments
    let commentCount = 0;
    estraverse.traverse(ast, {
      enter: (node: any) => {
        if (node.type === 'CommentBlock' || node.type === 'CommentLine') {
          commentCount++;
        }
      },
    });

    if (commentCount < lines / 10) {
      score -= 10;
    }

    // Check for long functions
    let longFunctionCount = 0;
    estraverse.traverse(ast, {
      enter: (node: any) => {
        if (
          (node.type === 'FunctionDeclaration' || node.type === 'FunctionExpression') &&
          node.loc.end.line - node.loc.start.line > 20
        ) {
          longFunctionCount++;
        }
      },
    });

    if (longFunctionCount > 0) {
      score -= 10 * longFunctionCount;
    }

    return Math.max(0, Math.min(100, score));
  }

  private analyzeCodePatterns(ast: any, issues: Array<{
    type: 'error' | 'warning' | 'info';
    message: string;
    line: number;
    column: number;
  }>) {
    // Check for duplicate code
    this.checkDuplicateCode(ast, issues);

    // Check for magic numbers
    this.checkMagicNumbers(ast, issues);

    // Check for long variable names
    this.checkVariableNames(ast, issues);

    // Check for error handling
    this.checkErrorHandling(ast, issues);
  }

  private checkDuplicateCode(ast: any, issues: Array<{
    type: 'error' | 'warning' | 'info';
    message: string;
    line: number;
    column: number;
  }>) {
    const codeBlocks = new Map<string, number>();

    estraverse.traverse(ast, {
      enter: (node: any) => {
        if (node.type === 'BlockStatement') {
          const code = escodegen.generate(node);
          const count = codeBlocks.get(code) || 0;
          codeBlocks.set(code, count + 1);

          if (count + 1 > 2) {
            issues.push({
              type: 'warning',
              message: 'Duplicate code block detected. Consider extracting to a function.',
              line: node.loc.start.line,
              column: node.loc.start.column,
            });
          }
        }
      },
    });
  }

  private checkMagicNumbers(ast: any, issues: Array<{
    type: 'error' | 'warning' | 'info';
    message: string;
    line: number;
    column: number;
  }>) {
    estraverse.traverse(ast, {
      enter: (node: any) => {
        if (node.type === 'Literal' && typeof node.value === 'number' && node.value > 10) {
          issues.push({
            type: 'warning',
            message: 'Magic number detected. Consider defining as a named constant.',
            line: node.loc.start.line,
            column: node.loc.start.column,
          });
        }
      },
    });
  }

  private checkVariableNames(ast: any, issues: Array<{
    type: 'error' | 'warning' | 'info';
    message: string;
    line: number;
    column: number;
  }>) {
    estraverse.traverse(ast, {
      enter: (node: any) => {
        if (node.type === 'VariableDeclarator' && node.id.name.length > 20) {
          issues.push({
            type: 'warning',
            message: 'Long variable name detected. Consider using a shorter, more descriptive name.',
            line: node.loc.start.line,
            column: node.loc.start.column,
          });
        }
      },
    });
  }

  private checkErrorHandling(ast: any, issues: Array<{
    type: 'error' | 'warning' | 'info';
    message: string;
    line: number;
    column: number;
  }>) {
    let hasTryCatch = false;

    estraverse.traverse(ast, {
      enter: (node: any) => {
        if (node.type === 'TryStatement') {
          hasTryCatch = true;
        }
      },
    });

    if (!hasTryCatch) {
      issues.push({
        type: 'warning',
        message: 'No error handling detected. Consider adding try-catch blocks for better error management.',
        line: 1,
        column: 1,
      });
    }
  }

  private async calculateTestCoverage(file: CodeFile): Promise<number> {
    // TODO: Implement actual test coverage calculation
    // This would involve running tests and collecting coverage data
    return 80; // Mock value for now
  }
} 