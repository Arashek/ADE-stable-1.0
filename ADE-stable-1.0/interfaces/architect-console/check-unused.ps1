# Install depcheck if not already installed
Write-Host "Checking for depcheck installation..."
if (-not (Get-Command "depcheck" -ErrorAction SilentlyContinue)) {
    Write-Host "Installing depcheck..."
    npm install -g depcheck
}

# Check for unused dependencies
Write-Host "Checking for unused dependencies..."
$unused = depcheck

# Check if unused dependencies were found
if ($LASTEXITCODE -eq 0) {
    Write-Host "No unused dependencies found!"
} else {
    Write-Host "Unused dependencies found:"
    $unused | ForEach-Object {
        Write-Host "- $_"
    }
    exit 1
} 