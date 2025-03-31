export interface RefactoringOperation {
  id: string;
  type: RefactoringType;
  description: string;
  file: string;
  line: number;
  preview?: string;
  status: 'pending' | 'applied' | 'failed';
  error?: string;
  parameters?: RefactoringParameters;
}

export type RefactoringType =
  | 'extract-method'
  | 'rename-symbol'
  | 'extract-variable'
  | 'inline-variable'
  | 'move-method'
  | 'change-signature';

export interface RefactoringParameters {
  // Extract Method parameters
  extractedMethodName?: string;
  selectedCode?: string;
  returnType?: string;
  methodParameters?: Array<{
    name: string;
    type: string;
  }>;

  // Rename Symbol parameters
  oldName?: string;
  newName?: string;
  symbolType?: 'variable' | 'function' | 'class' | 'interface' | 'type';

  // Extract Variable parameters
  expression?: string;
  variableName?: string;
  variableType?: string;

  // Inline Variable parameters
  variableToInline?: string;

  // Move Method parameters
  sourceClass?: string;
  targetClass?: string;
  methodToMove?: string;

  // Change Signature parameters
  targetMethodName?: string;
  newParameters?: Array<{
    name: string;
    type: string;
    defaultValue?: string;
  }>;
  newReturnType?: string;
} 