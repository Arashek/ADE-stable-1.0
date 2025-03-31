# Install package-size if not already installed
Write-Host "Checking for package-size installation..."
if (-not (Get-Command "package-size" -ErrorAction SilentlyContinue)) {
    Write-Host "Installing package-size..."
    npm install -g package-size
}

# Define size thresholds (in MB)
$warningThreshold = 10
$errorThreshold = 50

# Get package.json content
$packageJson = Get-Content "package.json" | ConvertFrom-Json

# Check size of each dependency
Write-Host "Checking dependency sizes..."
$largePackages = @()

foreach ($dependency in $packageJson.dependencies.PSObject.Properties) {
    $name = $dependency.Name
    Write-Host "Checking size of $name..."
    
    try {
        $size = package-size $name --json | ConvertFrom-Json
        $sizeInMB = [math]::Round($size.size / 1024 / 1024, 2)
        
        if ($sizeInMB -gt $errorThreshold) {
            $largePackages += "$name ($sizeInMB MB) - ERROR: Size exceeds $errorThreshold MB"
        }
        elseif ($sizeInMB -gt $warningThreshold) {
            $largePackages += "$name ($sizeInMB MB) - WARNING: Size exceeds $warningThreshold MB"
        }
    }
    catch {
        Write-Host "Failed to check size of $name"
    }
}

# Report results
if ($largePackages.Count -eq 0) {
    Write-Host "No large dependencies found!"
} else {
    Write-Host "Large dependencies found:"
    $largePackages | ForEach-Object {
        Write-Host "- $_"
    }
    exit 1
} 