# Clean the project
Write-Host "Cleaning the project..."
npm run clean

# Install dependencies
Write-Host "Installing dependencies..."
npm install

# Run TypeScript compiler in production mode
Write-Host "Running TypeScript compiler in production mode..."
npx tsc --noEmit

# Build the project for production
Write-Host "Building the project for production..."
npm run build

# Check if build was successful
if ($LASTEXITCODE -ne 0) {
    Write-Host "Build failed. Please fix the issues."
    exit 1
}

# Run tests
Write-Host "Running tests..."
npm run test

# Check if tests passed
if ($LASTEXITCODE -ne 0) {
    Write-Host "Tests failed. Please fix them."
    exit 1
}

# Check bundle size
Write-Host "Checking bundle size..."
npx vite-bundle-visualizer

# Optimize images
Write-Host "Optimizing images..."
npx imagemin public/**/*.{jpg,png,gif,svg} --out-dir=public/optimized

# Generate source maps
Write-Host "Generating source maps..."
npx vite build --sourcemap

Write-Host "Project optimization completed successfully!" 