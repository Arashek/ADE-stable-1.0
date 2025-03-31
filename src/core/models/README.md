# Project Context and Code Understanding

This module provides advanced code analysis and project context management capabilities for the ADE Platform.

## Overview

The module consists of two main components:

1. **ProjectContext**: Manages project-wide analysis and dependencies
2. **EnhancedCodeUnderstanding**: Provides detailed code analysis capabilities

## Features

### Project Context Management

- Cross-file dependency tracking
- Project-wide semantic analysis
- Dependency graph construction
- Cycle detection
- Topological sorting
- Strongly connected components analysis

### Code Understanding

- Language detection and configuration
- AST-based code analysis
- Semantic code analysis
- Control flow analysis
- Data flow analysis
- Style analysis
- Complexity analysis
- Security analysis
- Performance analysis

## Components

### ProjectContext

The `ProjectContext` class manages project-wide analysis and provides:

- Project file tracking
- Dependency management
- Semantic context building
- Project metrics calculation
- Symbol table management
- Type registry

### EnhancedCodeUnderstanding

The `EnhancedCodeUnderstanding` class provides detailed code analysis with:

- Language-specific analysis
- Pattern-based detection
- Entity extraction
- Dependency analysis
- Style checking
- Complexity metrics
- Security scanning
- Performance profiling

## Usage

### Basic Usage

```python
from core.models.project_context import ProjectContext
from core.models.enhanced_code_understanding import EnhancedCodeUnderstanding

# Initialize project context
context = ProjectContext(project_path)

# Analyze entire project
analysis = context.analyze_project()

# Get specific analysis
dependencies = context.get_dependencies()
semantic_info = context.get_semantic_info()
metrics = context.get_project_metrics()
```

### Code Analysis

```python
# Initialize code understanding
analyzer = EnhancedCodeUnderstanding()

# Analyze single file
file_analysis = analyzer.analyze_file(file_path)

# Get specific analysis
style = analyzer.analyze_style(ast)
complexity = analyzer.analyze_complexity(ast)
security = analyzer.analyze_security(ast)
performance = analyzer.analyze_performance(ast)
```

## Testing

The module includes comprehensive test suites:

1. **Unit Tests** (`test_enhanced_code_understanding.py`)
   - Basic functionality tests
   - Language detection tests
   - Analysis method tests

2. **Integration Tests** (`test_frontend_integration.py`)
   - Frontend component integration
   - Cross-component interaction
   - End-to-end analysis

3. **Stress Tests** (`test_project_context_stress.py`)
   - Massive project analysis
   - Concurrent processing
   - Memory management
   - Error recovery
   - Long-running stability

## Performance Considerations

- Memory usage is monitored and optimized
- Concurrent analysis is supported
- Large projects are handled efficiently
- Resource limits are enforced
- Error recovery is implemented

## Dependencies

- `ast` (Python standard library)
- `psutil` (for resource monitoring)
- `concurrent.futures` (for parallel processing)

## Contributing

When contributing to this module:

1. Follow the existing code style
2. Add comprehensive tests
3. Update documentation
4. Consider performance implications
5. Handle edge cases

## License

This module is part of the ADE Platform and follows its licensing terms. 