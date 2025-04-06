# ADE Platform - Test Environment Setup Script
# This script sets up a virtual environment and installs dependencies for local testing

$VenvPath = "venv"
$LogFile = "setup.log"

function Write-ColorOutput($ForegroundColor) {
    $fc = $host.UI.RawUI.ForegroundColor
    $host.UI.RawUI.ForegroundColor = $ForegroundColor
    if ($args) {
        Write-Output $args
    }
    else {
        $input | Write-Output
    }
    $host.UI.RawUI.ForegroundColor = $fc
}

function Log-Message {
    param (
        [Parameter(Mandatory=$true)]
        [string]$Message,
        
        [Parameter(Mandatory=$false)]
        [string]$Color = "White"
    )
    
    Write-ColorOutput $Color $Message
    Add-Content -Path $LogFile -Value "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') - $Message"
}

# Create log file
"$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') - Starting test environment setup" | Set-Content -Path $LogFile

# Check Python version
try {
    $pythonVersion = python --version
    Log-Message "Detected $pythonVersion" "Green"
} catch {
    Log-Message "Python not found. Please install Python 3.9+ before proceeding." "Red"
    exit 1
}

# Check if virtual environment exists
if (Test-Path $VenvPath) {
    Log-Message "Virtual environment already exists at $VenvPath" "Yellow"
    $recreate = Read-Host "Do you want to recreate it? (y/N)"
    if ($recreate -eq "y" -or $recreate -eq "Y") {
        Log-Message "Removing existing virtual environment..." "Yellow"
        Remove-Item -Recurse -Force $VenvPath
    } else {
        Log-Message "Using existing virtual environment" "Green"
        # Activate existing environment
        Log-Message "Activating virtual environment..." "Cyan"
        . ".\$VenvPath\Scripts\Activate.ps1"
        Log-Message "Environment activated" "Green"
        exit 0
    }
}

# Create virtual environment
Log-Message "Creating virtual environment in $VenvPath..." "Cyan"
try {
    python -m venv $VenvPath
    Log-Message "Virtual environment created successfully" "Green"
} catch {
    Log-Message "Failed to create virtual environment: $_" "Red"
    exit 1
}

# Activate virtual environment
Log-Message "Activating virtual environment..." "Cyan"
try {
    . ".\$VenvPath\Scripts\Activate.ps1"
    Log-Message "Virtual environment activated" "Green"
} catch {
    Log-Message "Failed to activate virtual environment: $_" "Red"
    exit 1
}

# Install dependencies
Log-Message "Installing dependencies from requirements.txt..." "Cyan"
try {
    pip install -r requirements.txt | Tee-Object -Append -FilePath $LogFile
    Log-Message "Dependencies installed successfully" "Green"
} catch {
    Log-Message "Failed to install dependencies: $_" "Red"
    exit 1
}

# Verify Pydantic installation
try {
    $pydanticVersion = pip show pydantic | Select-String "Version"
    Log-Message "Detected $pydanticVersion" "Green"
    
    if ($pydanticVersion -match "2\.") {
        Log-Message "Pydantic V2 detected, which is compatible with our codebase" "Green"
    } else {
        Log-Message "Warning: Using Pydantic V1. Some compatibility issues may occur." "Yellow"
    }
} catch {
    Log-Message "Failed to verify Pydantic version: $_" "Yellow"
}

Log-Message "Environment setup complete! You can now run the simplified backend with:" "Green"
Log-Message "python scripts\simplified_backend.py" "Cyan"
Log-Message "" 
Log-Message "To deactivate the virtual environment when finished, run:" "Green"
Log-Message "deactivate" "Cyan"
