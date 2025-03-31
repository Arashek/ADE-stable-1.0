# Install ts-unused-exports if not already installed
Write-Host "Checking for ts-unused-exports installation..."
if (-not (Get-Command "ts-unused-exports" -ErrorAction SilentlyContinue)) {
    Write-Host "Installing ts-unused-exports..."
    npm install -g ts-unused-exports
}

# Check for unused exports
Write-Host "Checking for unused exports..."
$unusedExports = ts-unused-exports tsconfig.json

# Check if unused exports were found
if ($LASTEXITCODE -eq 0) {
    Write-Host "No unused exports found!"
} else {
    Write-Host "Unused exports found:"
    $unusedExports | ForEach-Object {
        Write-Host "- $_"
    }
    exit 1
} 