# Check for security vulnerabilities
Write-Host "Checking for security vulnerabilities..."
$vulnerabilities = npm audit

# Check if vulnerabilities were found
if ($LASTEXITCODE -eq 0) {
    Write-Host "No security vulnerabilities found!"
} else {
    Write-Host "Security vulnerabilities found:"
    $vulnerabilities | ForEach-Object {
        Write-Host "- $_"
    }
    exit 1
} 