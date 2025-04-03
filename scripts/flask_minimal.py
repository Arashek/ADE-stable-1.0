#!/usr/bin/env python
"""
Flask Minimal API Server for ADE Platform

This is a minimal Flask API server for testing API functionality,
focusing on error logging and prompt processing.
"""

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import uuid
import time
import random
import threading
import logging
import os
import json
from datetime import datetime, timedelta
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# In-memory storage for prompt tasks (in a real application, this would be a database)
tasks = {}

# Enum-like constants for error categories and severities
class ErrorCategory:
    AGENT = "AGENT"
    API = "API"
    FRONTEND = "FRONTEND"
    SYSTEM = "SYSTEM"
    DATABASE = "DATABASE"

class ErrorSeverity:
    CRITICAL = "CRITICAL"
    ERROR = "ERROR"
    WARNING = "WARNING"
    INFO = "INFO"

# Paths for error logs
ADE_HOME = Path(__file__).resolve().parent.parent
ERROR_LOGS_DIR = ADE_HOME / "logs" / "errors"
ERROR_LOGS_FILE = ERROR_LOGS_DIR / "error_logs.json"

# Create directories if they don't exist
ERROR_LOGS_DIR.mkdir(parents=True, exist_ok=True)

# Initialize error logs file if it doesn't exist
if not ERROR_LOGS_FILE.exists():
    with open(ERROR_LOGS_FILE, 'w') as f:
        json.dump({"errors": []}, f)

# Function to log errors
def log_error(message, category, severity, component, context=None, stack_trace=None):
    """
    Log an error to the error logs file
    
    Args:
        message (str): The error message
        category (str): The error category (e.g., AGENT, API, FRONTEND)
        severity (str): The error severity (e.g., CRITICAL, ERROR, WARNING, INFO)
        component (str): The component where the error occurred
        context (dict, optional): Additional context information. Defaults to None.
        stack_trace (str, optional): Stack trace of the error. Defaults to None.
    
    Returns:
        dict: The logged error
    """
    try:
        # Load existing errors
        with open(ERROR_LOGS_FILE, 'r') as f:
            data = json.load(f)
        
        # Create new error entry
        error = {
            "id": str(uuid.uuid4()),
            "timestamp": datetime.now().isoformat(),
            "message": message,
            "category": category,
            "severity": severity,
            "component": component,
            "context": context or {},
            "stack_trace": stack_trace
        }
        
        # Add error to the list
        data["errors"].append(error)
        
        # Write back to file
        with open(ERROR_LOGS_FILE, 'w') as f:
            json.dump(data, f, indent=2)
        
        return error
    except Exception as e:
        logger.error(f"Failed to log error: {str(e)}")
        return None

# Function to get error logs
def get_error_logs():
    """
    Get all error logs
    
    Returns:
        dict: Error logs and statistics
    """
    try:
        with open(ERROR_LOGS_FILE, 'r') as f:
            data = json.load(f)
        
        errors = data.get("errors", [])
        
        # Calculate statistics
        total_errors = len(errors)
        severity_counts = {}
        category_counts = {}
        component_counts = {}
        recent_errors = 0
        
        # 24 hours ago
        day_ago = (datetime.now() - timedelta(days=1)).isoformat()
        
        for error in errors:
            # Count by severity
            severity = error.get("severity")
            if severity:
                severity_counts[severity] = severity_counts.get(severity, 0) + 1
            
            # Count by category
            category = error.get("category")
            if category:
                category_counts[category] = category_counts.get(category, 0) + 1
            
            # Count by component
            component = error.get("component")
            if component:
                component_counts[component] = component_counts.get(component, 0) + 1
            
            # Count recent errors
            if error.get("timestamp", "") >= day_ago:
                recent_errors += 1
        
        # Get top components
        top_components = [
            {"component": component, "count": count}
            for component, count in sorted(component_counts.items(), key=lambda x: x[1], reverse=True)
        ][:5]
        
        # Compile statistics
        stats = {
            "total": total_errors,
            "bySeverity": severity_counts,
            "byCategory": category_counts,
            "recentErrors": recent_errors,
            "topComponents": top_components
        }
        
        return {
            "errors": errors,
            "stats": stats
        }
    except Exception as e:
        logger.error(f"Failed to get error logs: {str(e)}")
        return {"errors": [], "stats": None}

# Function to clear error logs
def clear_error_logs():
    """
    Clear all error logs
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        with open(ERROR_LOGS_FILE, 'w') as f:
            json.dump({"errors": []}, f, indent=2)
        return True
    except Exception as e:
        logger.error(f"Failed to clear error logs: {str(e)}")
        return False

# Function to generate test error logs
def generate_test_error_logs(count=20):
    """
    Generate test error logs
    
    Args:
        count (int, optional): Number of test errors to generate. Defaults to 20.
    
    Returns:
        int: Number of errors generated
    """
    try:
        categories = [
            ErrorCategory.AGENT,
            ErrorCategory.API,
            ErrorCategory.FRONTEND,
            ErrorCategory.SYSTEM,
            ErrorCategory.DATABASE
        ]
        
        severities = [
            ErrorSeverity.CRITICAL,
            ErrorSeverity.ERROR,
            ErrorSeverity.WARNING,
            ErrorSeverity.INFO
        ]
        
        components = [
            "promptService",
            "apiClient",
            "errorLogger",
            "agentCoordinator",
            "databaseConnector",
            "userManager",
            "fileSystem",
            "configService",
            "uiComponents",
            "testHarness"
        ]
        
        error_messages = [
            "Failed to process prompt",
            "API request timed out",
            "Invalid configuration detected",
            "Database connection error",
            "User authentication failed",
            "File not found",
            "Invalid input format",
            "Response parsing error",
            "Agent initialization failed",
            "Network connectivity issue",
            "Memory allocation error",
            "Invalid state transition",
            "Resource unavailable",
            "Operation timed out",
            "Unexpected response format"
        ]
        
        contexts = [
            {"requestId": str(uuid.uuid4()), "endpoint": "/api/prompt"},
            {"userId": f"user_{random.randint(1000, 9999)}", "action": "login"},
            {"componentId": f"comp_{random.randint(100, 999)}", "state": "initializing"},
            {"fileId": f"file_{random.randint(100, 999)}", "path": "/tmp/test.txt"},
            {"transactionId": str(uuid.uuid4()), "table": "users"}
        ]
        
        stack_traces = [
            """File "/app/services/prompt_service.py", line 45, in process_prompt
    response = api_client.send_request(prompt)
  File "/app/clients/api_client.py", line 32, in send_request
    return self._parse_response(response)
  File "/app/clients/api_client.py", line 67, in _parse_response
    raise InvalidResponseError("Response validation failed")""",
            
            """File "/app/utils/db_connector.py", line 78, in execute_query
    connection = self.get_connection()
  File "/app/utils/db_connector.py", line 23, in get_connection
    return self.connection_pool.acquire()
  File "/app/utils/connection_pool.py", line 55, in acquire
    raise PoolExhaustedException("Connection pool exhausted")""",
            
            """File "/app/components/user_manager.py", line 156, in authenticate
    user = self.find_user(username)
  File "/app/components/user_manager.py", line 89, in find_user
    results = self.db.query("SELECT * FROM users WHERE username = %s", username)
  File "/app/utils/db_wrapper.py", line 45, in query
    cursor.execute(query, params)
sqlite3.OperationalError: database is locked"""
        ]
        
        # Generate random errors
        generated = 0
        for _ in range(count):
            # Random timestamp within the last 7 days
            timestamp_offset = random.randint(0, 7 * 24 * 60 * 60)
            timestamp = (datetime.now() - timedelta(seconds=timestamp_offset)).isoformat()
            
            category = random.choice(categories)
            severity = random.choice(severities)
            
            # More severe errors should be less frequent
            if severity == ErrorSeverity.CRITICAL and random.random() > 0.2:
                severity = ErrorSeverity.ERROR
            elif severity == ErrorSeverity.ERROR and random.random() > 0.4:
                severity = ErrorSeverity.WARNING
            
            component = random.choice(components)
            message = random.choice(error_messages)
            context = random.choice(contexts).copy()
            
            # Add some randomization to context
            context["timestamp"] = timestamp
            if random.random() > 0.7:
                context["additional"] = f"Additional info {random.randint(1, 100)}"
            
            # Only include stack trace for ERROR and CRITICAL
            stack_trace = None
            if severity in [ErrorSeverity.ERROR, ErrorSeverity.CRITICAL] and random.random() > 0.3:
                stack_trace = random.choice(stack_traces)
            
            # Log the error directly to file (bypassing the API)
            with open(ERROR_LOGS_FILE, 'r') as f:
                data = json.load(f)
            
            error = {
                "id": str(uuid.uuid4()),
                "timestamp": timestamp,
                "message": message,
                "category": category,
                "severity": severity,
                "component": component,
                "context": context,
                "stack_trace": stack_trace
            }
            
            data["errors"].append(error)
            
            with open(ERROR_LOGS_FILE, 'w') as f:
                json.dump(data, f, indent=2)
            
            generated += 1
        
        return generated
    except Exception as e:
        logger.error(f"Failed to generate test error logs: {str(e)}")
        return 0

# Function to simulate prompt processing
def process_prompt(prompt, context=None):
    """
    Simulate processing a prompt
    
    Args:
        prompt (str): The prompt to process
        context (dict, optional): Additional context. Defaults to None.
    
    Returns:
        str: Task ID for tracking the processing
    """
    task_id = str(uuid.uuid4())
    
    # Initialize task status
    tasks[task_id] = {
        "status": "submitted",
        "prompt": prompt,
        "context": context or {},
        "created_at": time.time(),
        "updated_at": time.time(),
        "progress": 0,
        "result": None,
        "message": "Prompt submitted successfully"
    }
    
    # Start processing in a background thread
    threading.Thread(target=_background_processing, args=(task_id,)).start()
    
    return task_id

# Background processing simulation
def _background_processing(task_id):
    """
    Simulate background processing of a prompt
    
    Args:
        task_id (str): The task ID to process
    """
    if task_id not in tasks:
        logger.error(f"Task {task_id} not found")
        return
    
    # Simulate processing steps
    steps = [
        {"status": "analyzing", "message": "Analyzing requirements", "duration": (1, 3)},
        {"status": "designing", "message": "Designing solution", "duration": (2, 4)},
        {"status": "generating", "message": "Generating code", "duration": (3, 5)},
        {"status": "finalizing", "message": "Finalizing and optimizing", "duration": (1, 2)}
    ]
    
    total_steps = len(steps)
    
    try:
        for i, step in enumerate(steps):
            # Update task status
            tasks[task_id].update({
                "status": step["status"],
                "message": step["message"],
                "progress": int((i / total_steps) * 100),
                "updated_at": time.time()
            })
            
            # Simulate processing time
            min_duration, max_duration = step["duration"]
            duration = min_duration + (max_duration - min_duration) * random.random()
            time.sleep(duration)
            
            # Randomly fail (10% chance)
            if random.random() < 0.1:
                tasks[task_id].update({
                    "status": "failed",
                    "message": f"Processing failed during {step['status']} step",
                    "updated_at": time.time()
                })
                
                # Log the error
                log_error(
                    f"Prompt processing failed during {step['status']} step",
                    ErrorCategory.API,
                    ErrorSeverity.ERROR,
                    "promptProcessor",
                    {
                        "task_id": task_id,
                        "prompt_preview": tasks[task_id]["prompt"][:50],
                        "step": step["status"]
                    }
                )
                
                return
        
        # Successfully completed
        tasks[task_id].update({
            "status": "completed",
            "message": "Processing completed successfully",
            "progress": 100,
            "updated_at": time.time(),
            "result": {
                "code": f'console.log("Generated from prompt: {tasks[task_id]["prompt"][:30]}...");\n\n// More code would be here in a real implementation',
                "description": "A simple application based on your prompt"
            }
        })
    except Exception as e:
        # Handle any unexpected errors
        error_message = f"Unexpected error during prompt processing: {str(e)}"
        
        tasks[task_id].update({
            "status": "failed",
            "message": error_message,
            "updated_at": time.time()
        })
        
        # Log the error
        log_error(
            error_message,
            ErrorCategory.SYSTEM,
            ErrorSeverity.ERROR,
            "promptProcessor",
            {
                "task_id": task_id,
                "exception": str(e)
            },
            "".join(traceback.format_exception(type(e), e, e.__traceback__))
        )

# API Routes

# Serve the error test page
@app.route('/error-test')
def serve_error_test_page():
    # Construct the path to the frontend/public directory
    public_dir = os.path.join(ADE_HOME, 'frontend', 'public')
    return send_from_directory(public_dir, 'error_test.html')

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "ok",
        "message": "ADE Flask API Server is running",
        "version": "1.0.0"
    })

@app.route('/api/prompt', methods=['POST'])
def submit_prompt():
    """Submit a prompt for processing"""
    data = request.json
    
    if not data or 'prompt' not in data:
        return jsonify({
            "status": "error",
            "message": "No prompt provided"
        }), 400
    
    prompt = data.get('prompt')
    context = data.get('context', {})
    
    # Log the submission
    logger.info(f"Received prompt: {prompt[:50]}...")
    
    # Process the prompt
    task_id = process_prompt(prompt, context)
    
    return jsonify({
        "status": "submitted",
        "task_id": task_id,
        "message": "Prompt submitted successfully"
    })

@app.route('/api/prompt/<task_id>', methods=['GET'])
def get_prompt_status(task_id):
    """Get the status of a prompt processing task"""
    if task_id not in tasks:
        return jsonify({
            "status": "error",
            "message": f"Task {task_id} not found"
        }), 404
    
    return jsonify(tasks[task_id])

@app.route('/api/errors', methods=['GET'])
def get_errors():
    """Get all error logs"""
    return jsonify(get_error_logs())

@app.route('/api/errors', methods=['POST'])
def log_error_api():
    """Log an error"""
    data = request.json
    
    if not data:
        return jsonify({
            "status": "error",
            "message": "No data provided"
        }), 400
    
    message = data.get('message')
    category = data.get('category', ErrorCategory.SYSTEM)
    severity = data.get('severity', ErrorSeverity.ERROR)
    component = data.get('component', 'unknown')
    context = data.get('context')
    stack_trace = data.get('stack_trace')
    
    error = log_error(message, category, severity, component, context, stack_trace)
    
    if error:
        return jsonify({
            "status": "success",
            "message": "Error logged successfully",
            "error_id": error["id"]
        })
    else:
        return jsonify({
            "status": "error",
            "message": "Failed to log error"
        }), 500

@app.route('/api/errors', methods=['DELETE'])
def clear_errors():
    """Clear all error logs"""
    if clear_error_logs():
        return jsonify({
            "status": "success",
            "message": "Error logs cleared successfully"
        })
    else:
        return jsonify({
            "status": "error",
            "message": "Failed to clear error logs"
        }), 500

@app.route('/api/errors/generate-test-data', methods=['POST'])
def generate_test_errors():
    """Generate test error logs"""
    count = request.json.get('count', 20) if request.json else 20
    
    generated = generate_test_error_logs(count)
    
    return jsonify({
        "status": "success",
        "message": f"Generated {generated} test error logs",
        "count": generated
    })

if __name__ == '__main__':
    logger.info("Starting Flask server on port 8000")
    app.run(host='0.0.0.0', port=8000, debug=True)
