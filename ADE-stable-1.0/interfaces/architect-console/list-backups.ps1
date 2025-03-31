# List all backup directories
Write-Host "Available backups:"
Get-ChildItem -Directory -Filter "backup_*" | ForEach-Object {
    $backupDate = $_.Name -replace 'backup_(\d{8})_(\d{6})', '$1 $2'
    Write-Host "- $($_.Name) (Created: $backupDate)"
}

# Check if any backups were found
$backupCount = (Get-ChildItem -Directory -Filter "backup_*").Count
if ($backupCount -eq 0) {
    Write-Host "No backups found."
} 