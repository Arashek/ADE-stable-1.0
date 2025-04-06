# ADE Platform - Local Testing Plan

*Created: 2025-04-04*

This document outlines the steps to test the ADE platform locally, focusing on the core functionality of processing prompts and creating applications through the multi-agent system.

## Prerequisites

- Python 3.9+ with pip
- Node.js 16+ with npm
- All dependencies installed via `pip install -r backend/requirements.txt`
- All dependencies installed via `npm install` in the frontend directory

## Setting Up a Virtual Environment (Recommended)

Using a virtual environment is strongly recommended to isolate dependencies and prevent conflicts with other Python projects. Follow these steps to set up a virtual environment for the backend:

```powershell
# Navigate to the backend directory
cd d:\ADE-stable-1.0\backend

# Create a virtual environment
python -m venv venv

# Activate the virtual environment
.\venv\Scripts\Activate

# Install dependencies
pip install -r requirements.txt
```

Note: Always make sure to activate the virtual environment before running any Python scripts for the ADE platform. You'll know the virtual environment is active when you see `(venv)` at the beginning of your command prompt.

## Test Execution Steps

### Step 1: Start the Simplified Backend

The simplified backend includes only essential services needed for testing and features:
- Basic API endpoints for health checks, prompt processing, and status updates
- Minimal initialization to avoid complex service dependencies
- Better error handling and logging
- Health monitoring endpoint that provides detailed system information
- Pydantic V2 compatibility test endpoints to verify model schemas

```powershell
# Navigate to the backend directory
cd d:\ADE-stable-1.0\backend

# Activate the virtual environment if not already activated
.\venv\Scripts\Activate

# Start the simplified backend
python scripts\simplified_backend.py
```

Expected outcome:
- Backend server starts on http://localhost:8003
- Log messages show successful initialization of essential services
- No errors related to Pydantic V2 compatibility

### Step 2: Test Backend API Endpoints

Once the backend is running, test the API endpoints to verify they're working correctly:

```powershell
# Open a new PowerShell window
cd d:\ADE-stable-1.0\backend

# Activate the virtual environment
.\venv\Scripts\Activate

# Run the API endpoint tests
python scripts\test_api_endpoints.py
```

Expected outcome:
- All tests pass successfully
- Logs show successful responses from health, echo, prompt, and status endpoints

### Step 3: Start the Frontend Development Server

The frontend development server will allow us to test the user interface and integration with the backend:

```powershell
# Open a new PowerShell window
cd d:\ADE-stable-1.0\frontend

# Start the frontend development server with logging
.\scripts\start_frontend_with_logs.ps1
```

Expected outcome:
- Frontend development server starts on http://localhost:3000
- React application loads without errors in the browser
- Connection to backend is established

### Step 4: Use Diagnostic Tools to Verify System Status

We've added special diagnostic tools to help verify the system is working correctly:

1. **Diagnostic Panel**
   - Shows real-time backend connection status
   - Displays system health information including memory usage and CPU
   - Verifies that the frontend can communicate with the backend

2. **Pydantic V2 Compatibility Tester**
   - Validates the model and agent schemas using Pydantic V2 APIs
   - Tests that our updated models can properly validate input requests
   - Confirms that JSON schema generation works with the new syntax

To use these tools:
1. Navigate to http://localhost:3000 in your browser
2. Both diagnostic tools appear at the top of the home page
3. Use the buttons in each panel to test different aspects of the system

Expected outcome:
- Diagnostic Panel shows "Connected" status to the backend
- Pydantic V2 tests return successful results without errors
- Schema JSON structures are displayed correctly

### Step 5: Test End-to-End Prompt Processing

With both backend and frontend running, test the end-to-end workflow:

1. Navigate to http://localhost:3000 in your browser
2. Find the chat input or prompt area in the interface
3. Enter a test prompt like: "Create a simple React todo app"
4. Submit the prompt
5. Observe the status updates and response in the UI

Expected outcome:
- Prompt is sent to the backend successfully
- Status updates show progress (simulated or real)
- Eventual response or application generation is displayed

## Testing the Frontend

1. Start the frontend development server:
   ```powershell
   cd frontend
   $env:PORT=3002  # Use a specific port to avoid conflicts
   npm start
   ```

2. Open your browser and navigate to [http://localhost:3002](http://localhost:3002)

3. The frontend should load with the diagnostic tools visible at the top of the page:
   - SimpleDiagnostic - Basic connectivity test with minimal dependencies
   - DiagnosticPanel - Detailed backend connection status and API monitoring
   - PydanticTester - Test Pydantic V2 compatibility with backend models

4. Use the diagnostic tools to verify backend connectivity:
   - The "Check Backend Health" button in SimpleDiagnostic should display connection status
   - The DiagnosticPanel will show detailed information about backend services
   - Use the PydanticTester to validate that models are correctly serialized and deserialized

5. If you encounter any rendering issues:
   - Check the browser console for any JavaScript/TypeScript errors
   - Verify that the backend server is running on port 8003
   - Confirm that no TypeScript errors are present in the terminal where the frontend server is running

## Troubleshooting Common Issues

### Frontend Compilation Errors

#### Missing Imports in App.tsx
If you see errors like `Cannot find name 'Suspense'` or `Cannot find name 'CircularProgress'`, follow these steps:

1. Add the missing React imports at the top of App.tsx:
   ```tsx
   import React, { Suspense } from 'react';
   import { CircularProgress } from '@mui/material';
   ```

2. If you encounter additional compilation errors related to component imports, verify all required components are properly imported from their respective libraries.

3. For components like SimpleDiagnostic, DiagnosticPanel, and PydanticTester, ensure they are:
   - Correctly imported
   - Wrapped in error boundaries to prevent cascading failures
   - Rendered conditionally if dependencies are not yet available

#### TypeScript Type Errors
For type-related errors:

1. Check component prop types against their implementations
2. Use more specific types instead of 'any' where possible
3. Verify that all required props are being passed correctly
4. Use TypeScript's error messages to identify the exact line and issue that needs correction

#### Component Rendering Order
If components fail to render in the correct order:

1. Ensure that parent components are fully loaded before rendering children
2. Use React's useEffect with appropriate dependencies to control component initialization
3. Consider implementing loading states to handle asynchronous operations

### Backend Issues

- **Pydantic V2 Compatibility Errors**
  - Check that all models use `model_config` instead of `Config` class with `schema_extra`
  - Ensure validators are updated to use `field_validator` and `model_validator`

- **Import Errors**
  - Verify that utility modules are properly imported
  - Check for circular imports or missing dependencies

### Frontend Issues

- **Connection Errors**
  - Verify that the REACT_APP_API_URL environment variable points to the correct backend URL
  - Check CORS settings in the backend if cross-origin requests are failing

- **Rendering Issues**
  - Check browser console for JavaScript errors
  - Verify that all required components are properly imported

## Next Steps After Successful Testing

1. **Document Your Findings**: Note any issues or improvements needed
2. **Update Active Tasks**: Mark completed tasks and add new ones based on testing results
3. **Move Toward Full Integration**: Once simplified testing is successful, proceed with running the full system
4. **Prepare for Cloud Deployment**: Begin configuring cloud deployment components for cloudev.ai

## Test Data

For testing prompt processing, you can use the following prompts:

- "Create a simple React todo application with local storage"
- "Build a Python FastAPI backend for a blog"
- "Design a responsive landing page for a SaaS product"

These prompts should exercise different aspects of the agent system without being overly complex.
