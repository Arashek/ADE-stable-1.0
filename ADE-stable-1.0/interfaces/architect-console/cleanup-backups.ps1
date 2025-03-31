# Get the number of days to keep backups (default: 7)
param(
    [int]$daysToKeep = 7
)

# Get all backup directories
$backups = Get-ChildItem -Directory -Filter "backup_*"

# Calculate the cutoff date
$cutoffDate = (Get-Date).AddDays(-$daysToKeep)

# Remove old backups
$removedCount = 0
foreach ($backup in $backups) {
    $backupDate = [DateTime]::ParseExact(
        ($backup.Name -replace 'backup_(\d{8})_(\d{6})', '$1 $2'),
        "yyyyMMdd HHmmss",
        [System.Globalization.CultureInfo]::InvariantCulture
    )
    
    if ($backupDate -lt $cutoffDate) {
        Remove-Item -Path $backup.FullName -Recurse -Force
        $removedCount++
        Write-Host "Removed old backup: $($backup.Name)"
    }
}

Write-Host "Cleanup completed. Removed $removedCount old backup(s)." 