# Function to backup package files
function Backup-PackageFiles {
    Copy-Item "package.json" "package.json.backup"
    if (Test-Path "package-lock.json") {
        Copy-Item "package-lock.json" "package-lock.json.backup"
    }
}

# Function to restore package files
function Restore-PackageFiles {
    Move-Item "package.json.backup" "package.json" -Force
    if (Test-Path "package-lock.json.backup") {
        Move-Item "package-lock.json.backup" "package-lock.json" -Force
    }
}

# Install npm-check-updates if not already installed
Write-Host "Checking for npm-check-updates installation..."
if (-not (Get-Command "ncu" -ErrorAction SilentlyContinue)) {
    Write-Host "Installing npm-check-updates..."
    npm install -g npm-check-updates
}

# Backup current state
Write-Host "Backing up package files..."
Backup-PackageFiles

try {
    # Check for updates
    Write-Host "Checking for updates..."
    $updates = ncu

    if ($LASTEXITCODE -eq 0) {
        Write-Host "No updates available."
        exit 0
    }

    # Show available updates
    Write-Host "Available updates:"
    $updates | ForEach-Object {
        Write-Host "- $_"
    }

    # Update dependencies one by one
    Write-Host "Updating dependencies one by one..."
    $packageJson = Get-Content "package.json" | ConvertFrom-Json
    
    foreach ($dependency in $packageJson.dependencies.PSObject.Properties) {
        $name = $dependency.Name
        Write-Host "Updating $name..."
        
        # Update single dependency
        npm update $name
        
        # Run tests
        Write-Host "Running tests..."
        npm run test
        
        if ($LASTEXITCODE -ne 0) {
            Write-Host "Tests failed after updating $name. Rolling back..."
            Restore-PackageFiles
            npm install
            exit 1
        }
    }

    # Final test run
    Write-Host "Running final tests..."
    npm run test

    if ($LASTEXITCODE -eq 0) {
        Write-Host "All updates applied successfully!"
        Remove-Item "package.json.backup"
        Remove-Item "package-lock.json.backup" -ErrorAction SilentlyContinue
    } else {
        Write-Host "Final tests failed. Rolling back all changes..."
        Restore-PackageFiles
        npm install
        exit 1
    }
}
catch {
    Write-Host "An error occurred. Rolling back changes..."
    Restore-PackageFiles
    npm install
    exit 1
} 