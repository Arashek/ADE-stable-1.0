# Check if backup directory is provided
param(
    [Parameter(Mandatory=$true)]
    [string]$backupDir
)

# Check if backup directory exists
if (-not (Test-Path $backupDir)) {
    Write-Host "Backup directory '$backupDir' does not exist."
    exit 1
}

# Restore project files from backup
Write-Host "Restoring from backup..."
Copy-Item -Path "$backupDir/src" -Destination "." -Recurse -Force
Copy-Item -Path "$backupDir/public" -Destination "." -Recurse -Force
Copy-Item -Path "$backupDir/package.json" -Destination "." -Force
Copy-Item -Path "$backupDir/package-lock.json" -Destination "." -Force
Copy-Item -Path "$backupDir/tsconfig.json" -Destination "." -Force
Copy-Item -Path "$backupDir/vite.config.ts" -Destination "." -Force
Copy-Item -Path "$backupDir/*.ps1" -Destination "." -Force

# Check if restore was successful
if ($LASTEXITCODE -eq 0) {
    Write-Host "Restore completed successfully!"
} else {
    Write-Host "Failed to restore from backup. Please check the error messages above."
    exit 1
} 