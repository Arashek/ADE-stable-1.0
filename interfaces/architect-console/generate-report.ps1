# Create a report directory with timestamp
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$reportDir = "report_$timestamp"
New-Item -ItemType Directory -Path $reportDir

# Function to count lines in a file
function Get-LineCount {
    param($file)
    return (Get-Content $file).Count
}

# Function to count files by extension
function Get-FileCountByExtension {
    param($extension)
    return (Get-ChildItem -Recurse -File -Filter "*.$extension").Count
}

# Generate report content
$report = @"
# Project Report
Generated on: $(Get-Date)

## Project Statistics
- Total TypeScript files: $(Get-FileCountByExtension "ts")
- Total TypeScript React files: $(Get-FileCountByExtension "tsx")
- Total CSS files: $(Get-FileCountByExtension "css")
- Total lines of code: $((Get-ChildItem -Recurse -File -Include *.ts,*.tsx,*.css | ForEach-Object { Get-LineCount $_.FullName } | Measure-Object -Sum).Sum)

## Dependencies
$(npm list --depth=0 | Out-String)

## Scripts
$(Get-ChildItem -Filter "*.ps1" | ForEach-Object { "- $($_.Name)" } | Out-String)

## Project Structure
$(tree /F | Out-String)

## Recent Changes
$(git log --oneline -n 10 | Out-String)
"@

# Save report to file
$report | Out-File -FilePath "$reportDir/project_report.md"

# Check if report was generated successfully
if ($LASTEXITCODE -eq 0) {
    Write-Host "Project report generated successfully in $reportDir"
} else {
    Write-Host "Failed to generate project report. Please check the error messages above."
    exit 1
} 