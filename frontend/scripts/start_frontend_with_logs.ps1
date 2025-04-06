# ADE Platform - Frontend Development Script
# This script starts the frontend development server with logging

$LogFile = "frontend_dev_server.log"
$ErrorLogFile = "frontend_errors.log"

Write-Host "Starting ADE Platform Frontend Development Server..." -ForegroundColor Cyan
Write-Host "Logs will be written to $LogFile" -ForegroundColor Green
Write-Host "Errors will be written to $ErrorLogFile" -ForegroundColor Yellow

# Ensure node_modules exists
if (-not (Test-Path -Path "node_modules")) {
    Write-Host "Installing dependencies..." -ForegroundColor Magenta
    npm install | Tee-Object -FilePath $LogFile
}

# Set environment variables for API connection
$env:REACT_APP_API_URL = "http://localhost:8003/api"
$env:REACT_APP_WS_URL = "ws://localhost:8003"

# Start frontend server with logging
try {
    Write-Host "Starting frontend server..." -ForegroundColor Green
    npm start | Tee-Object -Append -FilePath $LogFile
} 
catch {
    $ErrorMessage = $_.Exception.Message
    Write-Host "Error starting frontend server: $ErrorMessage" -ForegroundColor Red
    $ErrorMessage | Out-File -Append -FilePath $ErrorLogFile
    
    # Provide troubleshooting tips
    Write-Host "`nTroubleshooting tips:" -ForegroundColor Yellow
    Write-Host "1. Make sure Node.js and npm are installed and up-to-date" -ForegroundColor Yellow
    Write-Host "2. Check for any errors in the frontend code" -ForegroundColor Yellow
    Write-Host "3. Try running 'npm install' manually to see detailed errors" -ForegroundColor Yellow
    Write-Host "4. Check package.json for any dependency issues" -ForegroundColor Yellow
}
