# Function to check if a command exists
function Test-Command {
    param($command)
    $oldPreference = $ErrorActionPreference
    $ErrorActionPreference = 'stop'
    try { if (Get-Command $command) { return $true } }
    catch { return $false }
    finally { $ErrorActionPreference = $oldPreference }
}

# Check Node.js version
Write-Host "Checking Node.js version..."
$nodeVersion = node --version
Write-Host "Node.js version: $nodeVersion"

# Check npm version
Write-Host "Checking npm version..."
$npmVersion = npm --version
Write-Host "npm version: $npmVersion"

# Check if required files exist
$requiredFiles = @(
    "package.json",
    "tsconfig.json",
    "vite.config.ts",
    "src/main.tsx",
    "src/App.tsx"
)

Write-Host "Checking required files..."
foreach ($file in $requiredFiles) {
    if (Test-Path $file) {
        Write-Host "✓ $file exists"
    } else {
        Write-Host "✗ $file is missing"
        exit 1
    }
}

# Check if node_modules exists
Write-Host "Checking node_modules..."
if (Test-Path "node_modules") {
    Write-Host "✓ node_modules exists"
} else {
    Write-Host "✗ node_modules is missing"
    Write-Host "Please run 'npm install' to install dependencies"
    exit 1
}

# Check if TypeScript is installed
Write-Host "Checking TypeScript installation..."
if (Test-Command "tsc") {
    Write-Host "✓ TypeScript is installed"
} else {
    Write-Host "✗ TypeScript is not installed"
    Write-Host "Please run 'npm install -g typescript' to install TypeScript"
    exit 1
}

# Check if Vite is installed
Write-Host "Checking Vite installation..."
if (Test-Command "vite") {
    Write-Host "✓ Vite is installed"
} else {
    Write-Host "✗ Vite is not installed"
    Write-Host "Please run 'npm install -g vite' to install Vite"
    exit 1
}

Write-Host "Health check completed successfully!" 