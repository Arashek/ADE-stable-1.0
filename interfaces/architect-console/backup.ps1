# Create a backup directory with timestamp
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$backupDir = "backup_$timestamp"

# Create the backup directory
New-Item -ItemType Directory -Path $backupDir

# Copy project files to backup directory
Write-Host "Creating backup..."
Copy-Item -Path "src" -Destination $backupDir -Recurse
Copy-Item -Path "public" -Destination $backupDir -Recurse
Copy-Item -Path "package.json" -Destination $backupDir
Copy-Item -Path "package-lock.json" -Destination $backupDir
Copy-Item -Path "tsconfig.json" -Destination $backupDir
Copy-Item -Path "vite.config.ts" -Destination $backupDir
Copy-Item -Path "*.ps1" -Destination $backupDir

# Check if backup was successful
if ($LASTEXITCODE -eq 0) {
    Write-Host "Backup created successfully in $backupDir"
} else {
    Write-Host "Failed to create backup. Please check the error messages above."
    exit 1
} 