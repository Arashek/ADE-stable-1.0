# Analysis Components Documentation

## Error Classifier

The Error Classifier is a component that analyzes and categorizes errors based on their characteristics, patterns, and context. It provides detailed classification information including category, subcategory, severity, impact level, and confidence score.

### Features

- **Comprehensive Error Categories**:
  - Runtime errors (TypeError, ValueError, etc.)
  - System errors (OSError, IOError, etc.)
  - Database errors (ConnectionError, TransactionError, etc.)
  - Network errors (ConnectionError, TimeoutError, etc.)
  - Security errors (AuthenticationError, AuthorizationError, etc.)
  - Performance errors (TimeoutError, ResourceExhaustedError, etc.)
  - Data errors (FormatError, EncodingError, etc.)
  - Infrastructure errors (DeploymentError, ConfigurationError, etc.)

- **Severity Levels**:
  - Critical: System crashes, data loss, security breaches
  - High: Performance degradation, partial outages
  - Medium: Reduced functionality, increased latency
  - Low: Non-critical failures, minor issues

- **Impact Levels**:
  - System-wide: Affects all users, core functionality
  - Service-level: Affects specific services
  - User-level: Affects specific users
  - Component-level: Affects single components

### Usage

```python
from src.core.analysis.error_classifier import ErrorClassifier

classifier = ErrorClassifier()

# Basic classification
error = "TypeError: 'NoneType' object is not subscriptable"
classification = classifier.classify_error(error)

# Classification with context
context = {
    "affects_all_users": True,
    "data_loss": True,
    "user_count": 1000
}
classification = classifier.classify_error(error, context=context)

# Classification with stack trace
stack_trace = [
    "File 'test.py', line 10, in process_data",
    "result = data['key']"
]
classification = classifier.classify_error(error, stack_trace=stack_trace)
```

## Code Structure Analyzer

The Code Structure Analyzer analyzes Python code organization, dependencies, and potential issues. It provides comprehensive metrics and insights about code quality, maintainability, and complexity.

### Features

- **Code Metrics**:
  - Total lines of code
  - Number of modules, classes, and functions
  - Average complexity per module
  - Lines per module/function/class

- **Complexity Analysis**:
  - Cyclomatic complexity calculation
  - Complexity distribution (low, medium, high, very high)
  - Complex function detection
  - Nested structure analysis

- **Dependency Analysis**:
  - Module dependencies
  - Circular dependency detection
  - Unused import detection
  - Dependency distribution

- **Code Quality Metrics**:
  - Docstring coverage
  - Complex functions ratio
  - Unused imports ratio
  - Circular dependencies count

- **Maintainability Metrics**:
  - Average function length
  - Average class size
  - Module size distribution
  - Code organization patterns

### Usage

```python
from src.core.analysis.code_structure_analyzer import CodeStructureAnalyzer

analyzer = CodeStructureAnalyzer()

# Analyze a directory
analysis = analyzer.analyze_directory("path/to/code")

# Access metrics
print(f"Total modules: {analysis.metrics['total_modules']}")
print(f"Total lines: {analysis.metrics['total_lines_of_code']}")
print(f"Average complexity: {analysis.metrics['average_complexity']:.2f}")

# Check for issues
if analysis.circular_dependencies:
    print("Circular dependencies found:")
    for cycle in analysis.circular_dependencies:
        print(f"  {' -> '.join(cycle)}")

if analysis.unused_imports:
    print("Unused imports found:")
    for module, imports in analysis.unused_imports.items():
        print(f"  {module}: {', '.join(imports)}")

# Generate report
report = analyzer.get_analysis_report(analysis)
print(report)
```

### Best Practices

1. **Error Classification**:
   - Provide detailed context for better classification
   - Include stack traces when available
   - Use consistent error message formats
   - Monitor classification confidence scores

2. **Code Structure Analysis**:
   - Run analysis regularly to track code quality
   - Address high complexity issues promptly
   - Maintain good documentation coverage
   - Avoid circular dependencies
   - Keep modules focused and cohesive

3. **Performance Considerations**:
   - Analysis can be time-consuming for large codebases
   - Consider running analysis in background
   - Cache analysis results when appropriate
   - Use incremental analysis for large changes

### Edge Cases and Limitations

1. **Error Classification**:
   - Empty or malformed error messages
   - Very long error messages
   - Special characters in error messages
   - Multiple patterns in single error
   - Invalid context data

2. **Code Structure Analysis**:
   - Empty files
   - Files with only comments
   - Invalid Python syntax
   - Very long lines
   - Mixed encodings
   - Large docstrings
   - Many imports
   - Complex inheritance
   - Decorators and metaprogramming

### Integration

Both components can be used together for comprehensive code analysis:

```python
from src.core.analysis.error_classifier import ErrorClassifier
from src.core.analysis.code_structure_analyzer import CodeStructureAnalyzer

# Initialize components
classifier = ErrorClassifier()
analyzer = CodeStructureAnalyzer()

# Analyze code structure
analysis = analyzer.analyze_directory("path/to/code")

# Classify any errors found
for module, issues in analysis.complex_functions.items():
    for issue in issues:
        classification = classifier.classify_error(
            f"Complex function detected: {issue}",
            context={"module": module}
        )
        print(f"Classification: {classification.category} - {classification.severity}")
``` 