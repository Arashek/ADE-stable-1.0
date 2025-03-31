# Function to measure execution time
function Measure-ExecutionTime {
    param($scriptBlock)
    $startTime = Get-Date
    & $scriptBlock
    $endTime = Get-Date
    return $endTime - $startTime
}

# Function to get memory usage
function Get-MemoryUsage {
    $process = Get-Process -Name "node"
    return $process.WorkingSet64 / 1MB
}

# Function to get CPU usage
function Get-CPUUsage {
    $process = Get-Process -Name "node"
    return $process.CPU
}

# Start monitoring
Write-Host "Starting performance monitoring..."
Write-Host "Press Ctrl+C to stop monitoring"

while ($true) {
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    
    # Get system metrics
    $memoryUsage = Get-MemoryUsage
    $cpuUsage = Get-CPUUsage
    
    # Get project metrics
    $buildTime = Measure-ExecutionTime { npm run build }
    $testTime = Measure-ExecutionTime { npm run test }
    
    # Display metrics
    Clear-Host
    Write-Host "Performance Metrics - $timestamp"
    Write-Host "------------------------"
    Write-Host "Memory Usage: $memoryUsage MB"
    Write-Host "CPU Usage: $cpuUsage%"
    Write-Host "Build Time: $($buildTime.TotalSeconds) seconds"
    Write-Host "Test Time: $($testTime.TotalSeconds) seconds"
    Write-Host "------------------------"
    Write-Host "Press Ctrl+C to stop monitoring"
    
    # Wait for 5 seconds before next measurement
    Start-Sleep -Seconds 5
} 