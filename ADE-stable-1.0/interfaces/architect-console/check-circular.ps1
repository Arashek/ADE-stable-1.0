# Install madge if not already installed
Write-Host "Checking for madge installation..."
if (-not (Get-Command "madge" -ErrorAction SilentlyContinue)) {
    Write-Host "Installing madge..."
    npm install -g madge
}

# Check for circular dependencies
Write-Host "Checking for circular dependencies..."
$circularDeps = madge --circular src/

# Check if circular dependencies were found
if ($LASTEXITCODE -eq 0) {
    Write-Host "No circular dependencies found!"
} else {
    Write-Host "Circular dependencies found:"
    $circularDeps | ForEach-Object {
        Write-Host "- $_"
    }
    exit 1
} 