# Function to check Node.js version compatibility
function Test-NodeVersion {
    $nodeVersion = node --version
    $requiredVersion = "14.0.0"
    
    if ([version]($nodeVersion -replace 'v','') -lt [version]$requiredVersion) {
        Write-Host "Warning: Node.js version $nodeVersion is below recommended version $requiredVersion"
        return $false
    }
    return $true
}

# Function to check TypeScript version compatibility
function Test-TypeScriptVersion {
    $tsVersion = tsc --version
    $requiredVersion = "4.0.0"
    
    if ([version]($tsVersion -replace 'Version ','') -lt [version]$requiredVersion) {
        Write-Host "Warning: TypeScript version $tsVersion is below recommended version $requiredVersion"
        return $false
    }
    return $true
}

# Function to check package version compatibility
function Test-PackageCompatibility {
    param($name, $version, $dependencies)
    
    foreach ($dep in $dependencies.PSObject.Properties) {
        $depName = $dep.Name
        $depVersion = $dep.Value
        
        # Check if dependency exists in package.json
        if ($packageJson.dependencies.$depName) {
            $installedVersion = $packageJson.dependencies.$depName -replace '[^0-9.]'
            $requiredVersion = $depVersion -replace '[^0-9.]'
            
            if ([version]$installedVersion -lt [version]$requiredVersion) {
                Write-Host "Warning: Package $name requires $depName@$depVersion but $installedVersion is installed"
                return $false
            }
        }
    }
    return $true
}

# Get package.json content
$packageJson = Get-Content "package.json" | ConvertFrom-Json

Write-Host "Checking dependency compatibility..."

# Check Node.js version
$nodeCompatible = Test-NodeVersion
if (-not $nodeCompatible) {
    Write-Host "Node.js version compatibility check failed"
}

# Check TypeScript version
$tsCompatible = Test-TypeScriptVersion
if (-not $tsCompatible) {
    Write-Host "TypeScript version compatibility check failed"
}

# Check each package's compatibility
$packagesCompatible = $true
foreach ($dependency in $packageJson.dependencies.PSObject.Properties) {
    $name = $dependency.Name
    $version = $dependency.Value
    
    Write-Host "Checking compatibility for $name@$version..."
    
    try {
        $packageInfo = npm view $name@$version dependencies --json | ConvertFrom-Json
        if (-not (Test-PackageCompatibility $name $version $packageInfo)) {
            $packagesCompatible = $false
        }
    }
    catch {
        Write-Host "Failed to check compatibility for $name"
        $packagesCompatible = $false
    }
}

# Report results
if ($nodeCompatible -and $tsCompatible -and $packagesCompatible) {
    Write-Host "All dependencies are compatible!"
    exit 0
} else {
    Write-Host "Some dependencies have compatibility issues. Please check the warnings above."
    exit 1
} 