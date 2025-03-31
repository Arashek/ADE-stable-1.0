# Function to measure package load time
function Measure-PackageLoadTime {
    param($package)
    
    $script = @"
console.time('$package');
require('$package');
console.timeEnd('$package');
"@
    
    $result = node -e $script 2>&1
    if ($result -match '${package}: ([0-9.]+)ms') {
        return [double]$matches[1]
    }
    return $null
}

# Function to measure package memory usage
function Measure-PackageMemoryUsage {
    param($package)
    
    $script = @"
const used = process.memoryUsage();
console.log('Before:', used.heapUsed);
require('$package');
const usedAfter = process.memoryUsage();
console.log('After:', usedAfter.heapUsed);
console.log('Difference:', usedAfter.heapUsed - used.heapUsed);
"@
    
    $result = node -e $script 2>&1
    if ($result -match 'Difference: ([0-9]+)') {
        return [long]$matches[1]
    }
    return $null
}

# Get package.json content
$packageJson = Get-Content "package.json" | ConvertFrom-Json

# Define performance thresholds
$loadTimeThreshold = 100 # ms
$memoryThreshold = 10 * 1024 * 1024 # 10MB

Write-Host "Checking dependency performance..."
$performanceIssues = @()

foreach ($dependency in $packageJson.dependencies.PSObject.Properties) {
    $name = $dependency.Name
    Write-Host "Analyzing $name..."
    
    # Measure load time
    $loadTime = Measure-PackageLoadTime $name
    if ($loadTime -and $loadTime -gt $loadTimeThreshold) {
        $performanceIssues += "$name (Load time: $loadTime ms)"
    }
    
    # Measure memory usage
    $memoryUsage = Measure-PackageMemoryUsage $name
    if ($memoryUsage -and $memoryUsage -gt $memoryThreshold) {
        $memoryUsageMB = [math]::Round($memoryUsage / 1024 / 1024, 2)
        $performanceIssues += "$name (Memory usage: $memoryUsageMB MB)"
    }
}

# Report results
if ($performanceIssues.Count -eq 0) {
    Write-Host "No performance issues found!"
    exit 0
} else {
    Write-Host "Performance issues found:"
    $performanceIssues | ForEach-Object {
        Write-Host "- $_"
    }
    exit 1
} 