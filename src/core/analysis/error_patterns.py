from typing import Dict, List, Any
from datetime import datetime
from .error_knowledge_base import ErrorPattern, ErrorSolution

def get_predefined_patterns() -> Dict[str, ErrorPattern]:
    """Get predefined error patterns."""
    return {
        # Runtime Errors
        "null_pointer": ErrorPattern(
            pattern_type="null_pointer",
            regex=r"TypeError: 'NoneType' object is not subscriptable",
            description="Attempting to access a method or attribute of a None object",
            severity="medium",
            category="runtime",
            subcategory="type_error",
            common_causes=["Uninitialized variable", "Missing return value", "Failed API call"],
            solutions=["sol_null_001", "sol_null_002"],
            examples=["data['key']", "obj.method()", "result.value"],
            created_at=datetime.now(),
            updated_at=datetime.now()
        ),
        "type_error": ErrorPattern(
            pattern_type="type_error",
            regex=r"TypeError: (.*) must be (.*), not (.*)",
            description="Invalid type provided for operation",
            severity="medium",
            category="runtime",
            subcategory="type_error",
            common_causes=["Wrong argument type", "Incorrect data format", "Type mismatch"],
            solutions=["sol_type_001", "sol_type_002"],
            examples=["int('abc')", "list + string", "dict['key'] = None"],
            created_at=datetime.now(),
            updated_at=datetime.now()
        ),
        "value_error": ErrorPattern(
            pattern_type="value_error",
            regex=r"ValueError: (.*)",
            description="Invalid value provided for operation",
            severity="medium",
            category="runtime",
            subcategory="value_error",
            common_causes=["Invalid input", "Out of range", "Empty value"],
            solutions=["sol_value_001", "sol_value_002"],
            examples=["int('abc')", "list.index(999)", "datetime.strptime('invalid', '%Y')"],
            created_at=datetime.now(),
            updated_at=datetime.now()
        ),
        
        # Database Errors
        "db_connection": ErrorPattern(
            pattern_type="db_connection",
            regex=r"DatabaseError: Connection refused",
            description="Failed to connect to database",
            severity="high",
            category="database",
            subcategory="connection_error",
            common_causes=["Invalid credentials", "Network issues", "Database down"],
            solutions=["sol_db_001", "sol_db_002"],
            examples=["db.connect()", "cursor.execute()", "connection.ping()"],
            created_at=datetime.now(),
            updated_at=datetime.now()
        ),
        "db_timeout": ErrorPattern(
            pattern_type="db_timeout",
            regex=r"OperationalError: timeout",
            description="Database operation timed out",
            severity="high",
            category="database",
            subcategory="timeout_error",
            common_causes=["Slow query", "Network latency", "Resource constraints"],
            solutions=["sol_db_003", "sol_db_004"],
            examples=["long_running_query()", "bulk_insert()", "complex_join()"],
            created_at=datetime.now(),
            updated_at=datetime.now()
        ),
        
        # Network Errors
        "connection_error": ErrorPattern(
            pattern_type="connection_error",
            regex=r"ConnectionError: (.*)",
            description="Failed to establish network connection",
            severity="high",
            category="network",
            subcategory="connection_error",
            common_causes=["Network down", "Firewall blocking", "Invalid URL"],
            solutions=["sol_net_001", "sol_net_002"],
            examples=["requests.get(url)", "socket.connect()", "http.client.connect()"],
            created_at=datetime.now(),
            updated_at=datetime.now()
        ),
        "timeout_error": ErrorPattern(
            pattern_type="timeout_error",
            regex=r"TimeoutError: (.*)",
            description="Network operation timed out",
            severity="high",
            category="network",
            subcategory="timeout_error",
            common_causes=["Slow response", "Network congestion", "Server overload"],
            solutions=["sol_net_003", "sol_net_004"],
            examples=["requests.get(url, timeout=5)", "socket.settimeout()"],
            created_at=datetime.now(),
            updated_at=datetime.now()
        ),
        
        # File System Errors
        "file_not_found": ErrorPattern(
            pattern_type="file_not_found",
            regex=r"FileNotFoundError: (.*)",
            description="File or directory not found",
            severity="medium",
            category="filesystem",
            subcategory="file_error",
            common_causes=["Wrong path", "Missing file", "Permission denied"],
            solutions=["sol_fs_001", "sol_fs_002"],
            examples=["open('missing.txt')", "os.remove('nonexistent')"],
            created_at=datetime.now(),
            updated_at=datetime.now()
        ),
        "permission_error": ErrorPattern(
            pattern_type="permission_error",
            regex=r"PermissionError: (.*)",
            description="Insufficient permissions for file operation",
            severity="high",
            category="filesystem",
            subcategory="permission_error",
            common_causes=["Read-only filesystem", "User permissions", "File locked"],
            solutions=["sol_fs_003", "sol_fs_004"],
            examples=["os.chmod()", "file.write()", "os.remove()"],
            created_at=datetime.now(),
            updated_at=datetime.now()
        ),
        
        # Memory Errors
        "memory_error": ErrorPattern(
            pattern_type="memory_error",
            regex=r"MemoryError: (.*)",
            description="Out of memory error",
            severity="critical",
            category="system",
            subcategory="memory_error",
            common_causes=["Large data processing", "Memory leak", "Resource exhaustion"],
            solutions=["sol_mem_001", "sol_mem_002"],
            examples=["large_list = [0] * 1000000000", "pandas.read_csv('huge.csv')"],
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
    }

def get_predefined_solutions() -> Dict[str, ErrorSolution]:
    """Get predefined error solutions."""
    return {
        # Null Pointer Solutions
        "sol_null_001": ErrorSolution(
            solution_id="sol_null_001",
            pattern_type="null_pointer",
            description="Add null check before access",
            steps=[
                "Identify the variable that might be None",
                "Add an explicit check using 'if variable is not None'",
                "Provide a default value or handle the None case",
                "Add logging to track when None values occur"
            ],
            prerequisites=["Access to source code", "Understanding of data flow"],
            success_criteria=[
                "No more NoneType errors",
                "Proper handling of None cases",
                "Logging of None occurrences"
            ],
            created_at=datetime.now(),
            updated_at=datetime.now()
        ),
        "sol_null_002": ErrorSolution(
            solution_id="sol_null_002",
            pattern_type="null_pointer",
            description="Initialize variables properly",
            steps=[
                "Review variable initialization points",
                "Ensure all variables are initialized before use",
                "Add default values where appropriate",
                "Consider using type hints for better tracking"
            ],
            prerequisites=["Access to source code", "Understanding of initialization flow"],
            success_criteria=[
                "All variables properly initialized",
                "No uninitialized variable access",
                "Type hints in place"
            ],
            created_at=datetime.now(),
            updated_at=datetime.now()
        ),
        
        # Database Connection Solutions
        "sol_db_001": ErrorSolution(
            solution_id="sol_db_001",
            pattern_type="db_connection",
            description="Verify database connection settings",
            steps=[
                "Check database credentials",
                "Verify network connectivity",
                "Confirm database service is running",
                "Test connection with minimal configuration"
            ],
            prerequisites=["Database credentials", "Network access", "Database admin access"],
            success_criteria=[
                "Successful connection test",
                "Proper credentials in place",
                "Network connectivity confirmed"
            ],
            created_at=datetime.now(),
            updated_at=datetime.now()
        ),
        "sol_db_002": ErrorSolution(
            solution_id="sol_db_002",
            pattern_type="db_connection",
            description="Implement connection retry logic",
            steps=[
                "Add retry mechanism with exponential backoff",
                "Set appropriate timeout values",
                "Implement proper error handling",
                "Add connection pooling if needed"
            ],
            prerequisites=["Access to connection code", "Understanding of retry patterns"],
            success_criteria=[
                "Successful connection after retries",
                "Proper error handling",
                "Improved connection stability"
            ],
            created_at=datetime.now(),
            updated_at=datetime.now()
        ),
        
        # Network Error Solutions
        "sol_net_001": ErrorSolution(
            solution_id="sol_net_001",
            pattern_type="connection_error",
            description="Implement robust network error handling",
            steps=[
                "Add comprehensive error handling",
                "Implement retry mechanism",
                "Add proper logging",
                "Consider circuit breaker pattern"
            ],
            prerequisites=["Access to network code", "Understanding of error handling"],
            success_criteria=[
                "Proper error handling in place",
                "Successful retry mechanism",
                "Comprehensive logging"
            ],
            created_at=datetime.now(),
            updated_at=datetime.now()
        ),
        
        # File System Solutions
        "sol_fs_001": ErrorSolution(
            solution_id="sol_fs_001",
            pattern_type="file_not_found",
            description="Implement proper file existence checks",
            steps=[
                "Add existence check before file operations",
                "Create necessary directories",
                "Handle missing files gracefully",
                "Add proper error messages"
            ],
            prerequisites=["Access to file operations", "Understanding of file system"],
            success_criteria=[
                "Proper file existence checks",
                "Graceful handling of missing files",
                "Clear error messages"
            ],
            created_at=datetime.now(),
            updated_at=datetime.now()
        ),
        
        # Memory Error Solutions
        "sol_mem_001": ErrorSolution(
            solution_id="sol_mem_001",
            pattern_type="memory_error",
            description="Implement memory optimization",
            steps=[
                "Review memory usage patterns",
                "Implement data streaming for large files",
                "Add memory monitoring",
                "Optimize data structures"
            ],
            prerequisites=["Access to code", "Understanding of memory management"],
            success_criteria=[
                "Reduced memory usage",
                "Successful large data processing",
                "Proper memory monitoring"
            ],
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
    } 