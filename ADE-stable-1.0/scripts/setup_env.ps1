# Script to set up environment variables from .env.txt file

# Function to check if .env.txt exists
function Test-EnvFile {
    if (-not (Test-Path ".env.txt")) {
        Write-Host "Error: .env.txt file not found in the current directory"
        return $false
    }
    return $true
}

# Function to read and set environment variables
function Set-EnvVariables {
    $envFile = Get-Content ".env.txt"
    $successCount = 0
    $errorCount = 0
    
    foreach ($line in $envFile) {
        # Skip empty lines and comments
        if ($line -match '^\s*$' -or $line -match '^\s*#') {
            continue
        }
        
        # Parse key-value pairs
        if ($line -match '^([^=]+)=(.*)$') {
            $key = $matches[1].Trim()
            $value = $matches[2].Trim()
            
            try {
                # Set environment variable for current user
                [System.Environment]::SetEnvironmentVariable($key, $value, "User")
                Write-Host "Successfully set $key"
                $successCount++
            }
            catch {
                Write-Host "Error setting $key : $_"
                $errorCount++
            }
        }
        else {
            Write-Host "Warning: Invalid line format: $line"
            $errorCount++
        }
    }
    
    return @{
        Success = $successCount
        Error = $errorCount
    }
}

# Function to verify environment variables
function Test-EnvVariables {
    $requiredVars = @(
        "OPENAI_API_KEY",
        "ANTHROPIC_API_KEY",
        "GOOGLE_API_KEY",
        "DEEPSEEK_API_KEY",
        "GROQ_API_KEY"
    )
    
    $missingVars = @()
    foreach ($var in $requiredVars) {
        if (-not [System.Environment]::GetEnvironmentVariable($var, "User")) {
            $missingVars += $var
        }
    }
    
    if ($missingVars.Count -gt 0) {
        Write-Host "`nMissing required environment variables:"
        foreach ($var in $missingVars) {
            Write-Host "- $var"
        }
        return $false
    }
    return $true
}

# Main script logic
Write-Host "Setting up environment variables from .env.txt..."

# Check if .env.txt exists
if (-not (Test-EnvFile)) {
    exit 1
}

# Set environment variables
$results = Set-EnvVariables

# Display results
Write-Host "`nEnvironment variable setup complete:"
Write-Host "Successfully set: $($results.Success) variables"
Write-Host "Errors: $($results.Error)"

# Verify required variables
Write-Host "`nVerifying required environment variables..."
if (Test-EnvVariables) {
    Write-Host "All required environment variables are set successfully."
}
else {
    Write-Host "Some required environment variables are missing. Please check the .env.txt file."
    exit 1
}

Write-Host "`nNote: You may need to restart your terminal for the changes to take effect." 