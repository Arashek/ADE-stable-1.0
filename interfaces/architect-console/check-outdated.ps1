# Check for outdated dependencies
Write-Host "Checking for outdated dependencies..."
$outdated = npm outdated

# Check if outdated dependencies were found
if ($LASTEXITCODE -eq 0) {
    Write-Host "No outdated dependencies found!"
} else {
    Write-Host "Outdated dependencies found:"
    $outdated | ForEach-Object {
        Write-Host "- $_"
    }
    exit 1
} 