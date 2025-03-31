# Install webpack-bundle-analyzer if not already installed
Write-Host "Checking for webpack-bundle-analyzer installation..."
if (-not (Get-Command "webpack-bundle-analyzer" -ErrorAction SilentlyContinue)) {
    Write-Host "Installing webpack-bundle-analyzer..."
    npm install -g webpack-bundle-analyzer
}

# Install source-map-explorer if not already installed
Write-Host "Checking for source-map-explorer installation..."
if (-not (Get-Command "source-map-explorer" -ErrorAction SilentlyContinue)) {
    Write-Host "Installing source-map-explorer..."
    npm install -g source-map-explorer
}

# Build the project with source maps
Write-Host "Building project with source maps..."
npm run build -- --sourcemap

# Define size thresholds (in KB)
$warningThreshold = 500 # 500KB
$errorThreshold = 1000 # 1MB

# Analyze bundle sizes
Write-Host "Analyzing bundle sizes..."
$largeFiles = @()

Get-ChildItem "dist/*.js" | ForEach-Object {
    $size = (Get-Item $_.FullName).Length / 1024 # Convert to KB
    $name = $_.Name
    
    if ($size -gt $errorThreshold) {
        $largeFiles += "$name ($([math]::Round($size, 2)) KB) - ERROR: Size exceeds $errorThreshold KB"
    }
    elseif ($size -gt $warningThreshold) {
        $largeFiles += "$name ($([math]::Round($size, 2)) KB) - WARNING: Size exceeds $warningThreshold KB"
    }
}

# Generate bundle analysis report
Write-Host "Generating bundle analysis report..."
webpack-bundle-analyzer dist/stats.json --port 8888 --report dist/bundle-report.html

# Generate source map analysis
Write-Host "Generating source map analysis..."
source-map-explorer dist/*.js --html > dist/source-map-report.html

# Report results
if ($largeFiles.Count -eq 0) {
    Write-Host "No large bundles found!"
    Write-Host "Bundle analysis report saved to dist/bundle-report.html"
    Write-Host "Source map analysis saved to dist/source-map-report.html"
    exit 0
} else {
    Write-Host "Large bundles found:"
    $largeFiles | ForEach-Object {
        Write-Host "- $_"
    }
    Write-Host "`nBundle analysis report saved to dist/bundle-report.html"
    Write-Host "Source map analysis saved to dist/source-map-report.html"
    Write-Host "`nConsider the following optimizations:"
    Write-Host "1. Use dynamic imports for large dependencies"
    Write-Host "2. Enable tree shaking"
    Write-Host "3. Split your bundles"
    Write-Host "4. Use compression"
    exit 1
} 