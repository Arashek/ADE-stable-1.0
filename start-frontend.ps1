# Kill any existing node processes to avoid port conflicts
taskkill /F /IM node.exe 2>$null

# Set environment variable for port
$env:PORT=3001

# Navigate to frontend directory
cd frontend

# Start the application
Write-Host "Starting frontend on port 3001..."
npm start
