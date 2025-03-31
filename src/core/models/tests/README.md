# Test Suite Documentation

This directory contains comprehensive test suites for the Project Context and Code Understanding modules.

## Test Structure

### 1. Unit Tests (`test_enhanced_code_understanding.py`)

Tests the core functionality of the code understanding system:

- Language detection
- AST parsing
- Code analysis methods
- Pattern matching
- Entity extraction

### 2. Integration Tests (`test_frontend_integration.py`)

Tests integration with frontend components:

- Frontend security analysis
- Frontend performance analysis
- Frontend style analysis
- Frontend complexity analysis
- Frontend entity analysis
- Frontend dependency analysis
- Frontend control flow analysis
- Frontend data flow analysis
- Frontend maintainability analysis
- Frontend test coverage analysis
- Frontend documentation analysis
- Frontend code quality analysis

### 3. Stress Tests (`test_project_context_stress.py`)

Tests system performance under heavy load:

- Massive project analysis (1000+ files)
- Concurrent analysis stress
- Memory management
- Error recovery
- Long-running analysis stability

## Test Data

Test data is stored in the `test_data` directory:

- `sample.py`: Sample Python file for testing
- `sample.js`: Sample JavaScript file for testing
- Additional test files are generated dynamically

## Running Tests

### Running All Tests

```bash
python -m unittest discover
```

### Running Specific Test Suite

```bash
# Run unit tests
python -m unittest test_enhanced_code_understanding.py

# Run integration tests
python -m unittest test_frontend_integration.py

# Run stress tests
python -m unittest test_project_context_stress.py
```

### Running Individual Tests

```bash
# Run specific test method
python -m unittest test_project_context_stress.TestProjectContextStress.test_massive_project_analysis
```

## Test Coverage

To generate test coverage reports:

```bash
coverage run -m unittest discover
coverage report
coverage html  # For HTML report
```

## Performance Benchmarks

Stress tests include performance benchmarks:

- Analysis time limits
- Memory usage thresholds
- Concurrent processing speed
- Resource utilization

## Test Dependencies

- `unittest` (Python standard library)
- `psutil` (for resource monitoring)
- `coverage` (for coverage reporting)
- `concurrent.futures` (for parallel testing)

## Adding New Tests

When adding new tests:

1. Follow the existing test structure
2. Include comprehensive assertions
3. Add appropriate test data
4. Consider edge cases
5. Document test purpose
6. Update this README

## Test Maintenance

Regular maintenance tasks:

1. Update test data as needed
2. Review and update assertions
3. Monitor test performance
4. Update documentation
5. Clean up test artifacts

## Troubleshooting

Common issues and solutions:

1. **Memory Issues**
   - Check resource limits
   - Review garbage collection
   - Monitor memory usage

2. **Performance Issues**
   - Review concurrent settings
   - Check file sizes
   - Monitor system resources

3. **Test Failures**
   - Check test data
   - Review assertions
   - Verify dependencies

## Contributing

When contributing tests:

1. Follow test naming conventions
2. Include docstrings
3. Add appropriate assertions
4. Handle cleanup properly
5. Update documentation 
 