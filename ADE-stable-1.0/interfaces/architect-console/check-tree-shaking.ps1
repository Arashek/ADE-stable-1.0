# Install webpack-bundle-analyzer if not already installed
Write-Host "Checking for webpack-bundle-analyzer installation..."
if (-not (Get-Command "webpack-bundle-analyzer" -ErrorAction SilentlyContinue)) {
    Write-Host "Installing webpack-bundle-analyzer..."
    npm install -g webpack-bundle-analyzer
}

# Function to check if a package supports tree shaking
function Test-TreeShaking {
    param($package)
    
    $packageJson = Get-Content "node_modules/$package/package.json" | ConvertFrom-Json
    
    # Check for "sideEffects" field
    if (Get-Member -InputObject $packageJson -Name "sideEffects") {
        return $true
    }
    
    # Check for "module" field (ESM support)
    if (Get-Member -InputObject $packageJson -Name "module") {
        return $true
    }
    
    # Check for "esm" field
    if (Get-Member -InputObject $packageJson -Name "esm") {
        return $true
    }
    
    return $false
}

# Get package.json content
$packageJson = Get-Content "package.json" | ConvertFrom-Json

Write-Host "Checking tree shaking support..."
$nonTreeShakeable = @()
$treeShakeable = @()

foreach ($dependency in $packageJson.dependencies.PSObject.Properties) {
    $name = $dependency.Name
    Write-Host "Analyzing $name..."
    
    if (Test-TreeShaking $name) {
        $treeShakeable += $name
    } else {
        $nonTreeShakeable += $name
    }
}

# Build project with bundle analyzer
Write-Host "Building project with bundle analyzer..."
$env:ANALYZE = "true"
npm run build

# Report results
Write-Host "`nTree Shaking Analysis Results:"
Write-Host "-----------------------------"

Write-Host "`nTree Shakeable Packages:"
$treeShakeable | ForEach-Object {
    Write-Host "✓ $_"
}

Write-Host "`nNon-Tree Shakeable Packages:"
$nonTreeShakeable | ForEach-Object {
    Write-Host "✗ $_"
}

Write-Host "`nRecommendations:"
Write-Host "1. Consider replacing non-tree shakeable packages with alternatives that support tree shaking"
Write-Host "2. Update packages to their latest versions as they might have added tree shaking support"
Write-Host "3. Check if you're using the ESM version of the packages"
Write-Host "4. Ensure your bundler is configured to perform tree shaking"

if ($nonTreeShakeable.Count -gt 0) {
    Write-Host "`nWarning: Some packages do not support tree shaking. This may lead to larger bundle sizes."
    exit 1
} else {
    Write-Host "`nAll packages support tree shaking!"
    exit 0
} 