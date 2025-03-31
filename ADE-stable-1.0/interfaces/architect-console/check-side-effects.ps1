# Function to check if a package has side effects
function Test-SideEffects {
    param($package)
    
    $packageJson = Get-Content "node_modules/$package/package.json" | ConvertFrom-Json
    
    # Check for "sideEffects" field
    if (Get-Member -InputObject $packageJson -Name "sideEffects") {
        if ($packageJson.sideEffects -eq $false) {
            return $false
        } elseif ($packageJson.sideEffects -is [Array]) {
            return $packageJson.sideEffects
        }
    }
    
    return $true
}

# Function to analyze imports for side effects
function Test-ImportSideEffects {
    param($file)
    
    $content = Get-Content $file
    $sideEffects = @()
    
    foreach ($line in $content) {
        if ($line -match "import\s+'([^']+)';" -or $line -match 'import\s+"([^"]+)";') {
            $import = $matches[1]
            if (-not ($import -match '^\.')) {
                $sideEffects += $import
            }
        }
    }
    
    return $sideEffects
}

# Get package.json content
$packageJson = Get-Content "package.json" | ConvertFrom-Json

Write-Host "Checking for package side effects..."
$packagesWithSideEffects = @()
$packagesWithoutSideEffects = @()
$packagesWithPartialSideEffects = @()

foreach ($dependency in $packageJson.dependencies.PSObject.Properties) {
    $name = $dependency.Name
    Write-Host "Analyzing $name..."
    
    $sideEffects = Test-SideEffects $name
    if ($sideEffects -eq $false) {
        $packagesWithoutSideEffects += $name
    } elseif ($sideEffects -is [Array]) {
        $packagesWithPartialSideEffects += @{
            Name = $name
            Files = $sideEffects
        }
    } else {
        $packagesWithSideEffects += $name
    }
}

Write-Host "`nAnalyzing source files for side effects..."
$sourceFiles = Get-ChildItem -Recurse -Filter "*.ts" | Where-Object { $_.FullName -like "*src*" }
$fileImportSideEffects = @{}

foreach ($file in $sourceFiles) {
    $sideEffects = Test-ImportSideEffects $file.FullName
    if ($sideEffects.Count -gt 0) {
        $fileImportSideEffects[$file.Name] = $sideEffects
    }
}

# Report results
Write-Host "`nSide Effects Analysis Results:"
Write-Host "---------------------------"

Write-Host "`nPackages without side effects:"
$packagesWithoutSideEffects | ForEach-Object {
    Write-Host "✓ $_"
}

Write-Host "`nPackages with partial side effects:"
$packagesWithPartialSideEffects | ForEach-Object {
    Write-Host "! $($_.Name)"
    $_.Files | ForEach-Object {
        Write-Host "  - $_"
    }
}

Write-Host "`nPackages with side effects:"
$packagesWithSideEffects | ForEach-Object {
    Write-Host "✗ $_"
}

Write-Host "`nFiles with potential side effect imports:"
foreach ($file in $fileImportSideEffects.Keys) {
    Write-Host "`n${file}:"
    $fileImportSideEffects[$file] | ForEach-Object {
        Write-Host "  - $_"
    }
}

Write-Host "`nRecommendations:"
Write-Host "1. Consider using packages without side effects when possible"
Write-Host "2. Review imports in your source files for unnecessary side effects"
Write-Host "3. Use named imports instead of importing entire modules"
Write-Host "4. Consider adding 'sideEffects: false' to your package.json if your code has no side effects"

if ($packagesWithSideEffects.Count -gt 0) {
    Write-Host "`nWarning: Some packages have side effects. This may affect tree shaking and bundle size."
    exit 1
} else {
    Write-Host "`nNo packages with full side effects found!"
    exit 0
} 