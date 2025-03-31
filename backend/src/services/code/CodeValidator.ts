import { CodeImplementation, CodeFile } from '../../../frontend/src/services/CodeImplementationService';
import * as esprima from 'esprima';
import * as estraverse from 'estraverse';

interface ValidationResult {
  isValid: boolean;
  errors: string[];
}

export class CodeValidator {
  public async validateImplementation(implementation: CodeImplementation): Promise<ValidationResult> {
    const errors: string[] = [];

    // Validate implementation properties
    if (!implementation.id) {
      errors.push('Implementation ID is required');
    }
    if (!implementation.projectId) {
      errors.push('Project ID is required');
    }
    if (!implementation.name) {
      errors.push('Implementation name is required');
    }
    if (!implementation.description) {
      errors.push('Implementation description is required');
    }
    if (!Array.isArray(implementation.files)) {
      errors.push('Files must be an array');
    }
    if (!['draft', 'review', 'approved', 'implemented'].includes(implementation.status)) {
      errors.push('Invalid implementation status');
    }

    // Validate each file
    for (const file of implementation.files) {
      const fileValidation = await this.validateFile(file);
      if (!fileValidation.isValid) {
        errors.push(...fileValidation.errors.map(error => `File ${file.path}: ${error}`));
      }
    }

    // Validate feedback if present
    if (implementation.feedback) {
      const feedbackValidation = this.validateFeedback(implementation.feedback);
      if (!feedbackValidation.isValid) {
        errors.push(...feedbackValidation.errors);
      }
    }

    return {
      isValid: errors.length === 0,
      errors,
    };
  }

  private async validateFile(file: CodeFile): Promise<ValidationResult> {
    const errors: string[] = [];

    // Validate file properties
    if (!file.id) {
      errors.push('File ID is required');
    }
    if (!file.path) {
      errors.push('File path is required');
    }
    if (!file.content) {
      errors.push('File content is required');
    }
    if (!file.language) {
      errors.push('File language is required');
    }
    if (!Array.isArray(file.dependencies)) {
      errors.push('Dependencies must be an array');
    }
    if (!(file.lastModified instanceof Date)) {
      errors.push('Last modified date must be a valid Date object');
    }

    // Validate file content syntax
    try {
      const ast = esprima.parseScript(file.content, {
        loc: true,
        range: true,
        comment: true,
      });

      // Check for common issues
      this.checkCommonIssues(ast, errors);
    } catch (error) {
      errors.push(`Syntax error: ${error.message}`);
    }

    return {
      isValid: errors.length === 0,
      errors,
    };
  }

  private validateFeedback(feedback: Array<{
    id: string;
    from: string;
    comment: string;
    timestamp: Date;
    status: 'pending' | 'resolved';
  }>): ValidationResult {
    const errors: string[] = [];

    for (const item of feedback) {
      if (!item.id) {
        errors.push('Feedback ID is required');
      }
      if (!item.from) {
        errors.push('Feedback author is required');
      }
      if (!item.comment) {
        errors.push('Feedback comment is required');
      }
      if (!(item.timestamp instanceof Date)) {
        errors.push('Feedback timestamp must be a valid Date object');
      }
      if (!['pending', 'resolved'].includes(item.status)) {
        errors.push('Invalid feedback status');
      }
    }

    return {
      isValid: errors.length === 0,
      errors,
    };
  }

  private checkCommonIssues(ast: any, errors: string[]) {
    // Check for console.log statements
    let hasConsoleLog = false;
    estraverse.traverse(ast, {
      enter: (node: any) => {
        if (
          node.type === 'CallExpression' &&
          node.callee.type === 'MemberExpression' &&
          node.callee.object.name === 'console' &&
          node.callee.property.name === 'log'
        ) {
          hasConsoleLog = true;
        }
      },
    });

    if (hasConsoleLog) {
      errors.push('Console.log statements should be removed from production code');
    }

    // Check for TODO comments
    let hasTodo = false;
    estraverse.traverse(ast, {
      enter: (node: any) => {
        if (node.type === 'CommentBlock' || node.type === 'CommentLine') {
          if (node.value.toLowerCase().includes('todo')) {
            hasTodo = true;
          }
        }
      },
    });

    if (hasTodo) {
      errors.push('TODO comments should be addressed before production');
    }

    // Check for empty catch blocks
    let hasEmptyCatch = false;
    estraverse.traverse(ast, {
      enter: (node: any) => {
        if (
          node.type === 'CatchClause' &&
          node.body.body.length === 0
        ) {
          hasEmptyCatch = true;
        }
      },
    });

    if (hasEmptyCatch) {
      errors.push('Empty catch blocks should be avoided');
    }

    // Check for unused variables
    const declaredVariables = new Set<string>();
    const usedVariables = new Set<string>();

    estraverse.traverse(ast, {
      enter: (node: any) => {
        if (node.type === 'VariableDeclarator' && node.id.type === 'Identifier') {
          declaredVariables.add(node.id.name);
        }
        if (node.type === 'Identifier') {
          usedVariables.add(node.name);
        }
      },
    });

    for (const variable of declaredVariables) {
      if (!usedVariables.has(variable)) {
        errors.push(`Unused variable: ${variable}`);
      }
    }
  }
} 