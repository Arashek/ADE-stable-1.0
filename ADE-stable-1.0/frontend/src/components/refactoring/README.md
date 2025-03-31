# Code Refactoring Feature

The code refactoring feature provides a comprehensive set of tools for safely transforming code while maintaining its behavior. This feature is implemented as a React component that integrates with the ADE platform's code editor.

## Components

### RefactoringPanel

The main component that provides the user interface for code refactoring operations. It includes:

- A grid of available refactoring operations
- Detailed view of selected operation
- Preview functionality
- Operation history with undo/redo support
- Error handling and status feedback

### RefactoringService

A singleton service that manages refactoring operations and maintains the operation history. It provides:

- Operation application
- Preview generation
- History management
- Undo/redo functionality

## Available Refactoring Operations

1. **Extract Method**
   - Extracts selected code into a new method
   - Automatically handles parameter extraction
   - Updates all call sites

2. **Rename Symbol**
   - Renames variables, functions, classes, interfaces, and types
   - Updates all references
   - Handles scope-aware renaming

3. **Extract Variable**
   - Extracts expressions into new variables
   - Handles type inference
   - Updates all usages

4. **Inline Variable**
   - Replaces variable usage with its value
   - Removes variable declaration
   - Updates all references

5. **Move Method**
   - Moves methods between classes
   - Updates all references
   - Handles access modifiers

6. **Change Signature**
   - Modifies method parameters and return type
   - Updates all call sites
   - Handles default values

## Usage

```typescript
import { RefactoringPanel } from './components/refactoring/RefactoringPanel';
import { useRefactoring } from './hooks/useRefactoring';

function CodeEditor() {
  const {
    applyRefactoring,
    previewRefactoring,
    undo,
    redo,
    isLoading,
    error
  } = useRefactoring();

  return (
    <RefactoringPanel
      onApplyRefactoring={applyRefactoring}
      onPreviewRefactoring={previewRefactoring}
      onUndo={undo}
      onRedo={redo}
    />
  );
}
```

## Testing

The feature includes comprehensive tests for both the UI component and the service:

```bash
# Run all tests
npm test

# Run specific test files
npm test RefactoringPanel.test.tsx
npm test RefactoringService.test.ts
```

## Contributing

When adding new refactoring operations:

1. Add the operation type to `RefactoringType` in `types/refactoring.ts`
2. Add operation parameters to `RefactoringParameters` interface
3. Implement the operation in `RefactoringService`
4. Add UI support in `RefactoringPanel`
5. Add tests for the new operation

## Best Practices

1. Always preview changes before applying them
2. Use undo/redo for safety
3. Check operation history for tracking changes
4. Handle errors gracefully
5. Provide clear feedback to users

## Limitations

1. Some operations may require additional context from the codebase
2. Complex refactorings may need manual verification
3. Performance may be affected by large codebases
4. Some language-specific features may not be supported

## Future Improvements

1. Add support for more refactoring operations
2. Improve performance for large codebases
3. Add support for batch operations
4. Enhance preview functionality
5. Add support for custom refactoring rules 