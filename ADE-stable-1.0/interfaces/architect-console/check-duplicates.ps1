# Install npm-check-duplicates if not already installed
Write-Host "Checking for npm-check-duplicates installation..."
if (-not (Get-Command "npm-check-duplicates" -ErrorAction SilentlyContinue)) {
    Write-Host "Installing npm-check-duplicates..."
    npm install -g npm-check-duplicates
}

# Check for duplicate dependencies
Write-Host "Checking for duplicate dependencies..."
$duplicates = npm-check-duplicates

# Check if duplicates were found
if ($LASTEXITCODE -eq 0) {
    Write-Host "No duplicate dependencies found!"
} else {
    Write-Host "Duplicate dependencies found:"
    $duplicates | ForEach-Object {
        Write-Host "- $_"
    }
    exit 1
} 