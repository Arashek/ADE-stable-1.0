# Install npm-audit if not already installed
Write-Host "Checking for npm-audit installation..."
if (-not (Get-Command "npm-audit" -ErrorAction SilentlyContinue)) {
    Write-Host "Installing npm-audit..."
    npm install -g npm-audit
}

# Check for dependency vulnerabilities
Write-Host "Checking for dependency vulnerabilities..."
$vulnerabilities = npm audit

# Check if vulnerabilities were found
if ($LASTEXITCODE -eq 0) {
    Write-Host "No dependency vulnerabilities found!"
} else {
    Write-Host "Dependency vulnerabilities found:"
    $vulnerabilities | ForEach-Object {
        Write-Host "- $_"
    }
    exit 1
} 