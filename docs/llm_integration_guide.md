# LLM Integration and Vector Store Guide

This guide provides comprehensive documentation for using the LLM integration and vector store features in the error analysis system.

## Table of Contents
1. [Setup and Configuration](#setup-and-configuration)
2. [LLM Client Usage](#llm-client-usage)
3. [Vector Store Usage](#vector-store-usage)
4. [Advanced Features](#advanced-features)
5. [Best Practices](#best-practices)
6. [Troubleshooting](#troubleshooting)

## Setup and Configuration

### Prerequisites
- Python 3.8 or higher
- OpenAI API key
- Required packages (see `requirements.txt`)

### Configuration
The system uses a JSON configuration file (`config.json`) for settings:

```json
{
    "llm": {
        "model": "gpt-4",
        "temperature": 0.2,
        "max_tokens": 1000,
        "top_p": 0.95,
        "frequency_penalty": 0.0,
        "presence_penalty": 0.0,
        "stop": null
    },
    "vector_store": {
        "index_path": "data/error_embeddings.index",
        "dimension": 1536,
        "similarity_threshold": 0.8,
        "max_results": 5,
        "save_interval": 100
    },
    "error_analysis": {
        "min_confidence": 0.7,
        "max_contributing_factors": 5,
        "max_suggested_fixes": 3,
        "context_window": 1000
    }
}
```

## LLM Client Usage

### Basic Error Analysis

```python
from src.core.llm.llm_client import LLMClient

# Initialize client
llm_client = LLMClient("path/to/config.json")

# Analyze a single error
error_message = "TypeError: 'NoneType' object is not subscriptable"
stack_trace = [
    "File 'test.py', line 10, in process_data",
    "result = data['key']",
    "TypeError: 'NoneType' object is not subscriptable"
]
patterns = [
    {
        "type": "type_error",
        "description": "Attempting to access dictionary key on None value"
    }
]
context = {
    "file": "test.py",
    "function": "process_data",
    "line": 10
}

analysis = llm_client.analyze_error(
    error_message,
    stack_trace,
    patterns,
    context
)

print(f"Primary cause: {analysis.primary_cause}")
print(f"Confidence: {analysis.confidence_score}")
print(f"Suggested fixes: {analysis.suggested_fixes}")
```

### Batch Error Analysis

```python
# Analyze multiple errors
errors = [
    {
        "message": "TypeError: 'NoneType' object is not subscriptable",
        "type": "TypeError",
        "context": {"file": "test1.py", "line": 10}
    },
    {
        "message": "ValueError: Invalid input format",
        "type": "ValueError",
        "context": {"file": "test2.py", "line": 15}
    }
]

analyses = llm_client.analyze_errors_batch(errors, batch_size=2)
for analysis in analyses:
    print(f"Error analysis: {analysis.primary_cause}")
```

### Error Fix Generation

```python
# Generate fix for an error
error = {
    "message": "IndexError: list index out of range",
    "type": "IndexError",
    "location": "test.py:20",
    "context": {
        "list_length": 0,
        "attempted_index": 5
    }
}

fix = llm_client.generate_error_fix(error)
print(f"Fix code: {fix['code']}")
print(f"Explanation: {fix['explanation']}")
```

### Error Prevention Suggestions

```python
# Get prevention suggestions
patterns = [
    {
        "type": "null_pointer",
        "frequency": 5,
        "description": "Accessing properties of null objects"
    },
    {
        "type": "index_error",
        "frequency": 3,
        "description": "Accessing invalid array indices"
    }
]

suggestions = llm_client.suggest_error_prevention(patterns)
print(f"Prevention strategies: {suggestions['strategies']}")
print(f"Best practices: {suggestions['best_practices']}")
```

## Vector Store Usage

### Basic Operations

```python
from src.core.llm.vector_store import VectorStore
import numpy as np

# Initialize vector store
vector_store = VectorStore("path/to/index")

# Add error embedding
error_id = "error_1"
embedding = np.random.rand(1536).astype(np.float32)  # Your embedding
metadata = {
    "error_type": "TypeError",
    "severity": 1,
    "location": "test.py:10"
}
vector_store.add_error(error_id, embedding, metadata)

# Find similar errors
similar_errors = vector_store.find_similar_errors(
    embedding,
    k=5,
    threshold=0.8
)
```

### Error Clustering

```python
# Cluster similar errors
clusters = vector_store.cluster_errors(
    n_clusters=5,
    min_cluster_size=2
)

print(f"Total clusters: {clusters['statistics']['total_clusters']}")
for cluster_id, error_ids in clusters['clusters'].items():
    print(f"Cluster {cluster_id}: {len(error_ids)} errors")
```

### Trend Analysis

```python
# Analyze error trends
trends = vector_store.analyze_error_trends(time_window=7)

print(f"Total errors in window: {trends['total_errors']}")
for error_type, trend_data in trends['trends'].items():
    print(f"{error_type}: {trend_data['frequency']} errors/day")
```

### Metadata Filtering

```python
# Filter errors by metadata
criteria = {
    "error_type": "TypeError",
    "severity": 1
}
matches = vector_store.filter_by_metadata(criteria)

for match in matches:
    print(f"Error ID: {match['error_id']}")
    print(f"Metadata: {match['metadata']}")
```

### Error Statistics

```python
# Get basic statistics
stats = vector_store.get_error_statistics()
print(f"Total errors: {stats['total_errors']}")
print(f"Error types: {stats['error_types']}")

# Get grouped statistics
grouped_stats = vector_store.get_error_statistics(group_by="error_type")
for error_type, type_stats in grouped_stats['grouped_statistics'].items():
    print(f"\n{error_type}:")
    print(f"Count: {type_stats['count']}")
    print(f"Severity distribution: {type_stats['severity_distribution']}")
```

## Advanced Features

### Custom Error Analysis
You can extend the error analysis by adding custom fields to the `ErrorAnalysis` dataclass:

```python
@dataclass
class CustomErrorAnalysis(ErrorAnalysis):
    custom_field: str
    additional_metrics: Dict[str, float]
```

### Custom Vector Store Index
You can use different FAISS index types for specific use cases:

```python
# Use IVF index for large-scale similarity search
index = faiss.IndexIVFFlat(faiss.IndexFlatL2(1536), 1536, 100, faiss.METRIC_L2)
vector_store.index = index
```

## Best Practices

1. **Error Analysis**
   - Provide complete context for better analysis
   - Use consistent error type naming
   - Include relevant code snippets

2. **Vector Store**
   - Regular index maintenance
   - Appropriate similarity thresholds
   - Metadata consistency

3. **Performance**
   - Batch operations for multiple errors
   - Efficient clustering parameters
   - Regular index optimization

4. **Security**
   - Secure API key management
   - Data privacy considerations
   - Access control implementation

## Troubleshooting

### Common Issues

1. **LLM API Errors**
   - Check API key configuration
   - Verify rate limits
   - Monitor token usage

2. **Vector Store Issues**
   - Index corruption
   - Memory constraints
   - Dimension mismatches

3. **Performance Problems**
   - Large index size
   - Inefficient clustering
   - Memory leaks

### Solutions

1. **API Issues**
   ```python
   # Implement retry logic
   from tenacity import retry, stop_after_attempt, wait_exponential
   
   @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
   def analyze_with_retry(self, error):
       return self.analyze_error(error)
   ```

2. **Index Issues**
   ```python
   # Rebuild corrupted index
   vector_store._rebuild_index()
   ```

3. **Performance Optimization**
   ```python
   # Use efficient index type
   index = faiss.IndexIVFPQ(faiss.IndexFlatL2(1536), 1536, 100, 8, 8)
   vector_store.index = index
   ```

## Support

For additional support:
- Check the [GitHub repository](https://github.com/your-repo)
- Join the [Discord community](https://discord.gg/your-server)
- Contact support at support@example.com 