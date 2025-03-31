import os
import shutil
import logging
import subprocess
from typing import Dict, List, Optional
from datetime import datetime
import json
import hashlib
from pathlib import Path

logger = logging.getLogger(__name__)

class BackupManager:
    def __init__(self, backup_dir: str = "backups"):
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        self._initialize_backup_dir()

    def _initialize_backup_dir(self):
        """Initialize backup directory structure"""
        try:
            # Create necessary subdirectories
            (self.backup_dir / "database").mkdir(exist_ok=True)
            (self.backup_dir / "files").mkdir(exist_ok=True)
            (self.backup_dir / "config").mkdir(exist_ok=True)
            (self.backup_dir / "logs").mkdir(exist_ok=True)
            logger.info("Backup directory structure initialized")
        except Exception as e:
            logger.error(f"Error initializing backup directory: {str(e)}")
            raise

    async def create_backup(self, backup_type: str = "full") -> str:
        """Create a system backup"""
        try:
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            backup_id = f"backup_{timestamp}_{backup_type}"
            backup_path = self.backup_dir / backup_id
            backup_path.mkdir(exist_ok=True)

            # Create backup manifest
            manifest = {
                "backup_id": backup_id,
                "type": backup_type,
                "timestamp": timestamp,
                "components": []
            }

            # Backup database
            if backup_type in ["full", "database"]:
                await self._backup_database(backup_path, manifest)

            # Backup files
            if backup_type in ["full", "files"]:
                await self._backup_files(backup_path, manifest)

            # Backup configuration
            if backup_type in ["full", "config"]:
                await self._backup_config(backup_path, manifest)

            # Backup logs
            if backup_type in ["full", "logs"]:
                await self._backup_logs(backup_path, manifest)

            # Save manifest
            manifest_path = backup_path / "manifest.json"
            with open(manifest_path, "w") as f:
                json.dump(manifest, f, indent=2)

            # Create backup archive
            archive_path = self.backup_dir / f"{backup_id}.tar.gz"
            self._create_archive(backup_path, archive_path)

            # Cleanup temporary files
            shutil.rmtree(backup_path)

            logger.info(f"Backup created successfully: {backup_id}")
            return backup_id
        except Exception as e:
            logger.error(f"Error creating backup: {str(e)}")
            raise

    async def restore_backup(self, backup_id: str) -> None:
        """Restore system from backup"""
        try:
            # Verify backup exists
            archive_path = self.backup_dir / f"{backup_id}.tar.gz"
            if not archive_path.exists():
                raise FileNotFoundError(f"Backup {backup_id} not found")

            # Extract backup
            temp_path = self.backup_dir / f"temp_{backup_id}"
            temp_path.mkdir(exist_ok=True)
            self._extract_archive(archive_path, temp_path)

            # Load manifest
            manifest_path = temp_path / "manifest.json"
            with open(manifest_path, "r") as f:
                manifest = json.load(f)

            # Restore components
            for component in manifest["components"]:
                if component["type"] == "database":
                    await self._restore_database(temp_path, component)
                elif component["type"] == "files":
                    await self._restore_files(temp_path, component)
                elif component["type"] == "config":
                    await self._restore_config(temp_path, component)
                elif component["type"] == "logs":
                    await self._restore_logs(temp_path, component)

            # Cleanup
            shutil.rmtree(temp_path)

            logger.info(f"Backup restored successfully: {backup_id}")
        except Exception as e:
            logger.error(f"Error restoring backup: {str(e)}")
            raise

    async def _backup_database(self, backup_path: Path, manifest: Dict) -> None:
        """Backup database"""
        try:
            db_path = backup_path / "database"
            db_path.mkdir(exist_ok=True)

            # Execute database backup command
            # This is a placeholder - implement actual database backup logic
            subprocess.run(["pg_dump", "-Fc", "-f", str(db_path / "database.dump")])

            manifest["components"].append({
                "type": "database",
                "path": "database/database.dump",
                "size": os.path.getsize(db_path / "database.dump")
            })
        except Exception as e:
            logger.error(f"Error backing up database: {str(e)}")
            raise

    async def _backup_files(self, backup_path: Path, manifest: Dict) -> None:
        """Backup files"""
        try:
            files_path = backup_path / "files"
            files_path.mkdir(exist_ok=True)

            # Copy files to backup directory
            # This is a placeholder - implement actual file backup logic
            shutil.copytree("data", files_path / "data")

            manifest["components"].append({
                "type": "files",
                "path": "files/data",
                "size": self._get_directory_size(files_path / "data")
            })
        except Exception as e:
            logger.error(f"Error backing up files: {str(e)}")
            raise

    async def _backup_config(self, backup_path: Path, manifest: Dict) -> None:
        """Backup configuration"""
        try:
            config_path = backup_path / "config"
            config_path.mkdir(exist_ok=True)

            # Copy configuration files
            # This is a placeholder - implement actual config backup logic
            shutil.copy("config.json", config_path / "config.json")

            manifest["components"].append({
                "type": "config",
                "path": "config/config.json",
                "size": os.path.getsize(config_path / "config.json")
            })
        except Exception as e:
            logger.error(f"Error backing up configuration: {str(e)}")
            raise

    async def _backup_logs(self, backup_path: Path, manifest: Dict) -> None:
        """Backup logs"""
        try:
            logs_path = backup_path / "logs"
            logs_path.mkdir(exist_ok=True)

            # Copy log files
            # This is a placeholder - implement actual log backup logic
            shutil.copytree("logs", logs_path / "logs")

            manifest["components"].append({
                "type": "logs",
                "path": "logs/logs",
                "size": self._get_directory_size(logs_path / "logs")
            })
        except Exception as e:
            logger.error(f"Error backing up logs: {str(e)}")
            raise

    async def _restore_database(self, backup_path: Path, component: Dict) -> None:
        """Restore database"""
        try:
            # Execute database restore command
            # This is a placeholder - implement actual database restore logic
            subprocess.run(["pg_restore", "-d", "database_name", str(backup_path / component["path"])])
        except Exception as e:
            logger.error(f"Error restoring database: {str(e)}")
            raise

    async def _restore_files(self, backup_path: Path, component: Dict) -> None:
        """Restore files"""
        try:
            # Restore files from backup
            # This is a placeholder - implement actual file restore logic
            shutil.rmtree("data", ignore_errors=True)
            shutil.copytree(backup_path / component["path"], "data")
        except Exception as e:
            logger.error(f"Error restoring files: {str(e)}")
            raise

    async def _restore_config(self, backup_path: Path, component: Dict) -> None:
        """Restore configuration"""
        try:
            # Restore configuration files
            # This is a placeholder - implement actual config restore logic
            shutil.copy(backup_path / component["path"], "config.json")
        except Exception as e:
            logger.error(f"Error restoring configuration: {str(e)}")
            raise

    async def _restore_logs(self, backup_path: Path, component: Dict) -> None:
        """Restore logs"""
        try:
            # Restore log files
            # This is a placeholder - implement actual log restore logic
            shutil.rmtree("logs", ignore_errors=True)
            shutil.copytree(backup_path / component["path"], "logs")
        except Exception as e:
            logger.error(f"Error restoring logs: {str(e)}")
            raise

    def _create_archive(self, source_path: Path, archive_path: Path) -> None:
        """Create a tar.gz archive"""
        try:
            subprocess.run(["tar", "-czf", str(archive_path), "-C", str(source_path.parent), source_path.name])
        except Exception as e:
            logger.error(f"Error creating archive: {str(e)}")
            raise

    def _extract_archive(self, archive_path: Path, target_path: Path) -> None:
        """Extract a tar.gz archive"""
        try:
            subprocess.run(["tar", "-xzf", str(archive_path), "-C", str(target_path)])
        except Exception as e:
            logger.error(f"Error extracting archive: {str(e)}")
            raise

    def _get_directory_size(self, directory: Path) -> int:
        """Calculate directory size"""
        try:
            total_size = 0
            for dirpath, dirnames, filenames in os.walk(directory):
                for f in filenames:
                    fp = os.path.join(dirpath, f)
                    total_size += os.path.getsize(fp)
            return total_size
        except Exception as e:
            logger.error(f"Error calculating directory size: {str(e)}")
            raise

    def list_backups(self) -> List[Dict]:
        """List all available backups"""
        try:
            backups = []
            for archive in self.backup_dir.glob("*.tar.gz"):
                backup_id = archive.stem
                manifest_path = self.backup_dir / f"temp_{backup_id}/manifest.json"
                
                if manifest_path.exists():
                    with open(manifest_path, "r") as f:
                        manifest = json.load(f)
                        backups.append({
                            "id": backup_id,
                            "type": manifest["type"],
                            "timestamp": manifest["timestamp"],
                            "size": archive.stat().st_size
                        })
            return sorted(backups, key=lambda x: x["timestamp"], reverse=True)
        except Exception as e:
            logger.error(f"Error listing backups: {str(e)}")
            raise

    def delete_backup(self, backup_id: str) -> None:
        """Delete a backup"""
        try:
            archive_path = self.backup_dir / f"{backup_id}.tar.gz"
            if archive_path.exists():
                archive_path.unlink()
                logger.info(f"Backup deleted: {backup_id}")
            else:
                raise FileNotFoundError(f"Backup {backup_id} not found")
        except Exception as e:
            logger.error(f"Error deleting backup: {str(e)}")
            raise

    def verify_backup(self, backup_id: str) -> bool:
        """Verify backup integrity"""
        try:
            archive_path = self.backup_dir / f"{backup_id}.tar.gz"
            if not archive_path.exists():
                return False

            # Extract backup
            temp_path = self.backup_dir / f"temp_{backup_id}"
            temp_path.mkdir(exist_ok=True)
            self._extract_archive(archive_path, temp_path)

            # Verify manifest
            manifest_path = temp_path / "manifest.json"
            if not manifest_path.exists():
                return False

            with open(manifest_path, "r") as f:
                manifest = json.load(f)

            # Verify components
            for component in manifest["components"]:
                component_path = temp_path / component["path"]
                if not component_path.exists():
                    return False
                if component["type"] == "files" or component["type"] == "logs":
                    if self._get_directory_size(component_path) != component["size"]:
                        return False
                else:
                    if os.path.getsize(component_path) != component["size"]:
                        return False

            # Cleanup
            shutil.rmtree(temp_path)
            return True
        except Exception as e:
            logger.error(f"Error verifying backup: {str(e)}")
            return False

# Create a singleton instance
backup_manager = BackupManager()

async def create_backup(backup_type: str = "full") -> str:
    """Create a system backup"""
    return await backup_manager.create_backup(backup_type)

async def restore_backup(backup_id: str) -> None:
    """Restore system from backup"""
    await backup_manager.restore_backup(backup_id)

def list_backups() -> List[Dict]:
    """List all available backups"""
    return backup_manager.list_backups()

def delete_backup(backup_id: str) -> None:
    """Delete a backup"""
    backup_manager.delete_backup(backup_id)

def verify_backup(backup_id: str) -> bool:
    """Verify backup integrity"""
    return backup_manager.verify_backup(backup_id) 