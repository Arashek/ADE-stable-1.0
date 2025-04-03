# Frontend Error Detection and Fixing Script
# PowerShell Script

# Display banner
Write-Host "======================================================" -ForegroundColor Cyan
Write-Host "      ADE Platform Frontend Error Detection Tool      " -ForegroundColor Cyan
Write-Host "======================================================" -ForegroundColor Cyan
Write-Host ""

# Set current directory to the script location
$scriptPath = $MyInvocation.MyCommand.Path
$scriptDir = Split-Path $scriptPath
Set-Location (Split-Path $scriptDir)

# Navigate to frontend directory
$frontendDir = "frontend"
if (-not (Test-Path -Path $frontendDir)) {
    Write-Host "Error: Frontend directory not found at $frontendDir" -ForegroundColor Red
    exit 1
}

# Function to check and fix common frontend issues
function Repair-FrontendIssues {
    Write-Host "Checking for common frontend issues..." -ForegroundColor Yellow
    
    # Array to track fixed issues
    $fixedIssues = @()

    # Check for missing React imports in hook files
    $hookFiles = Get-ChildItem -Path "$frontendDir\src\hooks" -Filter "*.ts" -Recurse
    foreach ($file in $hookFiles) {
        $content = Get-Content -Path $file.FullName -Raw
        
        # Check if the file uses React hooks but doesn't import React
        if (($content -match "use[A-Z]") -and (-not ($content -match "import React"))) {
            Write-Host "  - Missing React import in $($file.Name)" -ForegroundColor Yellow
            
            # Add React import if needed
            $newContent = "import React from 'react';`n" + $content
            Set-Content -Path $file.FullName -Value $newContent
            
            $fixedIssues += "Added React import to $($file.Name)"
        }
    }
    
    # Check for TypeScript configuration issues
    $tsConfigPath = "$frontendDir\tsconfig.json"
    if (Test-Path -Path $tsConfigPath) {
        $tsConfig = Get-Content -Path $tsConfigPath -Raw | ConvertFrom-Json
        
        # Check for missing compiler options
        $modified = $false
        if (-not $tsConfig.compilerOptions.esModuleInterop) {
            $tsConfig.compilerOptions | Add-Member -NotePropertyName "esModuleInterop" -NotePropertyValue $true
            $modified = $true
            $fixedIssues += "Added esModuleInterop to tsconfig.json"
        }
        
        if (-not $tsConfig.compilerOptions.allowSyntheticDefaultImports) {
            $tsConfig.compilerOptions | Add-Member -NotePropertyName "allowSyntheticDefaultImports" -NotePropertyValue $true
            $modified = $true
            $fixedIssues += "Added allowSyntheticDefaultImports to tsconfig.json"
        }
        
        if ($modified) {
            Write-Host "  - Updating TypeScript configuration" -ForegroundColor Yellow
            $tsConfig | ConvertTo-Json -Depth 10 | Set-Content -Path $tsConfigPath
        }
    }
    
    # Check package.json for missing dependencies
    $packageJsonPath = "$frontendDir\package.json"
    if (Test-Path -Path $packageJsonPath) {
        $packageJson = Get-Content -Path $packageJsonPath -Raw | ConvertFrom-Json
        
        # List of common dependencies that might be missing
        $dependencies = @{
            "react" = "^18.2.0"
            "react-dom" = "^18.2.0"
            "socket.io-client" = "^4.7.2"
            "@types/react" = "^18.2.21"
            "@types/react-dom" = "^18.2.7"
        }
        
        $modified = $false
        foreach ($dep in $dependencies.GetEnumerator()) {
            if (-not $packageJson.dependencies.$($dep.Key)) {
                Write-Host "  - Missing dependency: $($dep.Key)" -ForegroundColor Yellow
                $packageJson.dependencies | Add-Member -NotePropertyName $dep.Key -NotePropertyValue $dep.Value
                $modified = $true
                $fixedIssues += "Added missing dependency: $($dep.Key)"
            }
        }
        
        if ($modified) {
            Write-Host "  - Updating package.json" -ForegroundColor Yellow
            $packageJson | ConvertTo-Json -Depth 10 | Set-Content -Path $packageJsonPath
        }
    }

    return $fixedIssues
}

# Function to run ESLint to detect and fix issues
function Invoke-ESLintFix {
    Write-Host "Running ESLint to detect and fix issues..." -ForegroundColor Yellow
    
    try {
        # Check if ESLint exists in the project
        $eslintPath = "$frontendDir\node_modules\.bin\eslint"
        if (Test-Path -Path $eslintPath) {
            # Run ESLint with --fix option
            Set-Location $frontendDir
            $output = & npm run lint:fix 2>&1
            Set-Location ..
            
            if ($LASTEXITCODE -eq 0) {
                Write-Host "  - ESLint completed successfully" -ForegroundColor Green
                return $true
            } else {
                Write-Host "  - ESLint found issues that couldn't be automatically fixed:" -ForegroundColor Yellow
                $output | ForEach-Object { Write-Host "    $_" -ForegroundColor Yellow }
                return $false
            }
        } else {
            Write-Host "  - ESLint not found in project. Setting up..." -ForegroundColor Yellow
            Set-Location $frontendDir
            & npm install eslint eslint-plugin-react eslint-plugin-react-hooks @typescript-eslint/eslint-plugin @typescript-eslint/parser --save-dev
            Set-Location ..
            return $false
        }
    } catch {
        Write-Host "  - Error running ESLint: $_" -ForegroundColor Red
        return $false
    }
}

# Function to run TypeScript type checking
function Test-TypeScript {
    Write-Host "Running TypeScript compiler to check for type errors..." -ForegroundColor Yellow
    
    try {
        Set-Location $frontendDir
        $output = & npm run tsc 2>&1
        Set-Location ..
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "  - TypeScript check completed successfully" -ForegroundColor Green
            return $true
        } else {
            Write-Host "  - TypeScript found type errors:" -ForegroundColor Yellow
            $output | ForEach-Object { Write-Host "    $_" -ForegroundColor Yellow }
            return $false
        }
    } catch {
        Write-Host "  - Error running TypeScript checker: $_" -ForegroundColor Red
        return $false
    }
}

# Main execution
try {
    # Step 1: Fix common frontend issues
    $fixedIssues = Repair-FrontendIssues
    
    # Step 2: Try building the frontend
    Write-Host "Building frontend to check for errors..." -ForegroundColor Yellow
    Set-Location $frontendDir
    $buildOutput = & npm run build 2>&1
    $buildSuccess = $LASTEXITCODE -eq 0
    Set-Location ..
    
    if ($buildSuccess) {
        Write-Host "Frontend builds successfully!" -ForegroundColor Green
    } else {
        Write-Host "Frontend build failed with errors:" -ForegroundColor Red
        $buildOutput | ForEach-Object { Write-Host "  $_" -ForegroundColor Red }
        
        # Step 3: Try to fix the issues
        Write-Host "Attempting to fix issues..." -ForegroundColor Yellow
        
        # Run ESLint fix
        $eslintSuccess = Invoke-ESLintFix
        
        # Run TypeScript check
        $typeCheckSuccess = Test-TypeScript
        
        # Add summary of fix attempts
        if ($eslintSuccess) {
            $fixedIssues += "ESLint auto-fixed some issues"
        }
        
        if ($typeCheckSuccess) {
            $fixedIssues += "TypeScript checks passed after fixes"
        }
        
        # Try building again
        Write-Host "Attempting to build frontend again..." -ForegroundColor Yellow
        Set-Location $frontendDir
        $buildOutput = & npm run build 2>&1
        $buildSuccess = $LASTEXITCODE -eq 0
        Set-Location ..
        
        if ($buildSuccess) {
            Write-Host "Frontend builds successfully after fixes!" -ForegroundColor Green
        } else {
            Write-Host "Frontend still has build errors after attempted fixes:" -ForegroundColor Red
            $buildOutput | ForEach-Object { Write-Host "  $_" -ForegroundColor Red }
        }
    }
    
    # Summary
    Write-Host ""
    Write-Host "Frontend Error Detection Summary:" -ForegroundColor Cyan
    Write-Host "------------------------------" -ForegroundColor Cyan
    
    if ($fixedIssues.Count -gt 0) {
        Write-Host "Issues fixed:" -ForegroundColor Green
        $fixedIssues | ForEach-Object { Write-Host "  - $_" -ForegroundColor Green }
    } else {
        Write-Host "No common issues detected or fixed." -ForegroundColor Green
    }
    
    Write-Host "Build Status: $(if ($buildSuccess) { 'SUCCESS' } else { 'FAILED' })" -ForegroundColor $(if ($buildSuccess) { 'Green' } else { 'Red' })
    
    if ($buildSuccess) {
        Write-Host "The frontend is now error-free and ready for deployment!" -ForegroundColor Green
        exit 0
    } else {
        Write-Host "The frontend still has errors that need to be fixed manually." -ForegroundColor Yellow
        Write-Host "Please check the error output above for details." -ForegroundColor Yellow
        exit 1
    }
} catch {
    Write-Host "Error running frontend error detection: $_" -ForegroundColor Red
    exit 1
}
