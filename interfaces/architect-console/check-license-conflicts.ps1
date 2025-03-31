# Define allowed licenses
$allowedLicenses = @(
    "MIT",
    "Apache-2.0",
    "BSD-2-Clause",
    "BSD-3-Clause",
    "ISC"
)

# Install license-checker if not already installed
Write-Host "Checking for license-checker installation..."
if (-not (Get-Command "license-checker" -ErrorAction SilentlyContinue)) {
    Write-Host "Installing license-checker..."
    npm install -g license-checker
}

# Check for dependency conflicts with licenses
Write-Host "Checking for dependency conflicts with licenses..."
$licenses = license-checker --json

# Convert JSON output to PowerShell object
$licensesObj = $licenses | ConvertFrom-Json

# Check each dependency's license
$conflicts = @()
foreach ($dependency in $licensesObj.PSObject.Properties) {
    $name = $dependency.Name
    $license = $dependency.Value.licenses
    
    if ($license -notin $allowedLicenses) {
        $conflicts += "$name ($license)"
    }
}

# Report results
if ($conflicts.Count -eq 0) {
    Write-Host "No dependency conflicts with licenses found!"
} else {
    Write-Host "Dependency conflicts with licenses found:"
    $conflicts | ForEach-Object {
        Write-Host "- $_"
    }
    exit 1
} 