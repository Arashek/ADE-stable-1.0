from typing import Dict, List, Optional, Union, Tuple
import logging
from dataclasses import dataclass
import json
import os
import shutil
import hashlib
import base64
from datetime import datetime, timedelta
import threading
import queue
import time
from pathlib import Path
import zipfile
import tarfile
from concurrent.futures import ThreadPoolExecutor

@dataclass
class BackupConfig:
    backup_dir: str
    retention_days: int = 30
    max_backups: int = 10
    compression_level: int = 6
    chunk_size: int = 1024 * 1024  # 1MB
    parallel_backups: bool = True
    verify_backups: bool = True
    encrypt_backups: bool = True
    backup_interval_hours: int = 24
    incremental_backups: bool = True
    backup_metadata: bool = True
    backup_logs: bool = True
    backup_temp_files: bool = False
    backup_compression: str = "zip"  # zip, tar.gz
    backup_verification: bool = True
    backup_encryption: bool = True
    backup_compression_level: int = 6
    backup_parallel: bool = True
    backup_retry_attempts: int = 3
    backup_retry_delay: int = 300  # 5 minutes

class BackupEngine:
    def __init__(self, config: Optional[BackupConfig] = None):
        self.config = config or BackupConfig(
            backup_dir=os.path.join(os.getcwd(), "backups")
        )
        self.logger = logging.getLogger(__name__)
        self._init_backup_system()
        self._setup_backup_queue()
        self._start_backup_thread()

    def _init_backup_system(self):
        """Initialize the backup system."""
        # Create backup directory if it doesn't exist
        os.makedirs(self.config.backup_dir, exist_ok=True)
        
        # Initialize backup metadata
        self.backup_metadata = self._load_backup_metadata()
        
        # Initialize backup queue
        self.backup_queue = queue.Queue()
        
        # Initialize backup thread
        self.backup_thread = None
        self.backup_running = False

    def _setup_backup_queue(self):
        """Setup the backup queue for handling backup requests."""
        self.backup_queue = queue.PriorityQueue()

    def _start_backup_thread(self):
        """Start the backup thread for processing backup requests."""
        self.backup_running = True
        self.backup_thread = threading.Thread(
            target=self._process_backup_queue,
            daemon=True
        )
        self.backup_thread.start()

    def _process_backup_queue(self):
        """Process backup requests from the queue."""
        while self.backup_running:
            try:
                # Get next backup request from queue
                priority, backup_request = self.backup_queue.get(timeout=1)
                
                # Process backup request
                self._process_backup_request(backup_request)
                
                # Mark task as done
                self.backup_queue.task_done()
                
            except queue.Empty:
                continue
            except Exception as e:
                self.logger.error(f"Error processing backup request: {e}")

    def _process_backup_request(self, request: Dict):
        """Process a single backup request."""
        try:
            # Create backup
            backup_path = self.create_backup(
                source_path=request["source_path"],
                backup_type=request.get("backup_type", "full"),
                metadata=request.get("metadata", {})
            )
            
            # Verify backup if enabled
            if self.config.verify_backups:
                self.verify_backup(backup_path)
            
            # Update backup metadata
            self._update_backup_metadata(backup_path)
            
            # Clean up old backups
            self.cleanup_old_backups()
            
        except Exception as e:
            self.logger.error(f"Error processing backup request: {e}")
            self._handle_backup_error(request, e)

    def _handle_backup_error(self, request: Dict, error: Exception):
        """Handle backup errors and retry if necessary."""
        retry_count = request.get("retry_count", 0)
        
        if retry_count < self.config.backup_retry_attempts:
            # Retry backup request
            request["retry_count"] = retry_count + 1
            self.backup_queue.put((request["priority"], request))
            
            # Log retry attempt
            self.logger.warning(
                f"Retrying backup request (attempt {retry_count + 1})"
            )
            
            # Wait before retry
            time.sleep(self.config.backup_retry_delay)
        else:
            # Log final failure
            self.logger.error(
                f"Backup request failed after {retry_count} attempts"
            )

    def create_backup(
        self,
        source_path: str,
        backup_type: str = "full",
        metadata: Optional[Dict] = None
    ) -> str:
        """Create a backup of the specified path."""
        # Generate backup filename
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"backup_{timestamp}_{backup_type}"
        
        # Create backup path
        backup_path = os.path.join(
            self.config.backup_dir,
            f"{backup_filename}.{self.config.backup_compression}"
        )
        
        # Create backup metadata
        backup_metadata = {
            "timestamp": timestamp,
            "backup_type": backup_type,
            "source_path": source_path,
            "compression": self.config.backup_compression,
            "compression_level": self.config.backup_compression_level,
            "chunk_size": self.config.chunk_size,
            "verify_backups": self.config.verify_backups,
            "encrypt_backups": self.config.encrypt_backups
        }
        
        if metadata:
            backup_metadata.update(metadata)
        
        # Create backup based on type
        if backup_type == "full":
            self._create_full_backup(source_path, backup_path, backup_metadata)
        elif backup_type == "incremental":
            self._create_incremental_backup(
                source_path,
                backup_path,
                backup_metadata
            )
        else:
            raise ValueError(f"Unsupported backup type: {backup_type}")
        
        return backup_path

    def _create_full_backup(
        self,
        source_path: str,
        backup_path: str,
        metadata: Dict
    ):
        """Create a full backup."""
        if self.config.backup_compression == "zip":
            self._create_zip_backup(source_path, backup_path, metadata)
        elif self.config.backup_compression == "tar.gz":
            self._create_tar_backup(source_path, backup_path, metadata)
        else:
            raise ValueError(
                f"Unsupported compression format: {self.config.backup_compression}"
            )

    def _create_incremental_backup(
        self,
        source_path: str,
        backup_path: str,
        metadata: Dict
    ):
        """Create an incremental backup."""
        if not self.config.incremental_backups:
            raise ValueError("Incremental backups are not enabled")
        
        # Get last backup timestamp
        last_backup = self._get_last_backup_timestamp()
        if not last_backup:
            # If no previous backup, create full backup
            self._create_full_backup(source_path, backup_path, metadata)
            return
        
        # Create incremental backup
        self._create_incremental_backup_impl(
            source_path,
            backup_path,
            last_backup,
            metadata
        )

    def _create_zip_backup(
        self,
        source_path: str,
        backup_path: str,
        metadata: Dict
    ):
        """Create a ZIP backup."""
        with zipfile.ZipFile(
            backup_path,
            "w",
            compression=zipfile.ZIP_DEFLATED,
            compresslevel=self.config.backup_compression_level
        ) as zip_file:
            # Add files to ZIP
            for root, _, files in os.walk(source_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, source_path)
                    zip_file.write(file_path, arcname)
            
            # Add metadata
            if self.config.backup_metadata:
                zip_file.writestr(
                    "backup_metadata.json",
                    json.dumps(metadata, indent=2)
                )

    def _create_tar_backup(
        self,
        source_path: str,
        backup_path: str,
        metadata: Dict
    ):
        """Create a TAR.GZ backup."""
        with tarfile.open(
            backup_path,
            "w:gz",
            compresslevel=self.config.backup_compression_level
        ) as tar_file:
            # Add files to TAR
            tar_file.add(source_path, arcname="")
            
            # Add metadata
            if self.config.backup_metadata:
                metadata_str = json.dumps(metadata, indent=2)
                metadata_info = tarfile.TarInfo("backup_metadata.json")
                metadata_info.size = len(metadata_str)
                tar_file.addfile(metadata_info, metadata_str.encode())

    def _create_incremental_backup_impl(
        self,
        source_path: str,
        backup_path: str,
        last_backup: datetime,
        metadata: Dict
    ):
        """Implementation of incremental backup creation."""
        # Get list of modified files
        modified_files = self._get_modified_files(source_path, last_backup)
        
        # Create incremental backup
        if self.config.backup_compression == "zip":
            self._create_incremental_zip_backup(
                source_path,
                backup_path,
                modified_files,
                metadata
            )
        elif self.config.backup_compression == "tar.gz":
            self._create_incremental_tar_backup(
                source_path,
                backup_path,
                modified_files,
                metadata
            )
        else:
            raise ValueError(
                f"Unsupported compression format: {self.config.backup_compression}"
            )

    def _get_modified_files(
        self,
        source_path: str,
        last_backup: datetime
    ) -> List[str]:
        """Get list of files modified since last backup."""
        modified_files = []
        
        for root, _, files in os.walk(source_path):
            for file in files:
                file_path = os.path.join(root, file)
                mtime = datetime.fromtimestamp(os.path.getmtime(file_path))
                
                if mtime > last_backup:
                    modified_files.append(file_path)
        
        return modified_files

    def verify_backup(self, backup_path: str) -> bool:
        """Verify the integrity of a backup."""
        try:
            # Check if backup exists
            if not os.path.exists(backup_path):
                raise FileNotFoundError(f"Backup not found: {backup_path}")
            
            # Verify based on compression type
            if self.config.backup_compression == "zip":
                return self._verify_zip_backup(backup_path)
            elif self.config.backup_compression == "tar.gz":
                return self._verify_tar_backup(backup_path)
            else:
                raise ValueError(
                    f"Unsupported compression format: {self.config.backup_compression}"
                )
        
        except Exception as e:
            self.logger.error(f"Backup verification failed: {e}")
            return False

    def _verify_zip_backup(self, backup_path: str) -> bool:
        """Verify a ZIP backup."""
        try:
            with zipfile.ZipFile(backup_path, "r") as zip_file:
                # Test ZIP integrity
                return zip_file.testzip() is None
        except Exception as e:
            self.logger.error(f"ZIP verification failed: {e}")
            return False

    def _verify_tar_backup(self, backup_path: str) -> bool:
        """Verify a TAR.GZ backup."""
        try:
            with tarfile.open(backup_path, "r:gz") as tar_file:
                # Test TAR integrity
                return tar_file.getmembers() is not None
        except Exception as e:
            self.logger.error(f"TAR verification failed: {e}")
            return False

    def restore_backup(
        self,
        backup_path: str,
        restore_path: str,
        verify: bool = True
    ) -> bool:
        """Restore a backup to the specified path."""
        try:
            # Verify backup if requested
            if verify and not self.verify_backup(backup_path):
                raise ValueError("Backup verification failed")
            
            # Create restore directory
            os.makedirs(restore_path, exist_ok=True)
            
            # Restore based on compression type
            if self.config.backup_compression == "zip":
                self._restore_zip_backup(backup_path, restore_path)
            elif self.config.backup_compression == "tar.gz":
                self._restore_tar_backup(backup_path, restore_path)
            else:
                raise ValueError(
                    f"Unsupported compression format: {self.config.backup_compression}"
                )
            
            return True
        
        except Exception as e:
            self.logger.error(f"Backup restoration failed: {e}")
            return False

    def _restore_zip_backup(self, backup_path: str, restore_path: str):
        """Restore a ZIP backup."""
        with zipfile.ZipFile(backup_path, "r") as zip_file:
            zip_file.extractall(restore_path)

    def _restore_tar_backup(self, backup_path: str, restore_path: str):
        """Restore a TAR.GZ backup."""
        with tarfile.open(backup_path, "r:gz") as tar_file:
            tar_file.extractall(restore_path)

    def cleanup_old_backups(self):
        """Clean up old backups based on retention policy."""
        try:
            # Get list of backups
            backups = self._get_backup_list()
            
            # Sort backups by timestamp
            backups.sort(key=lambda x: x["timestamp"], reverse=True)
            
            # Remove old backups
            current_time = datetime.utcnow()
            for backup in backups:
                backup_time = datetime.fromisoformat(backup["timestamp"])
                age = current_time - backup_time
                
                if age.days > self.config.retention_days:
                    self._remove_backup(backup["path"])
            
            # Remove excess backups
            if len(backups) > self.config.max_backups:
                for backup in backups[self.config.max_backups:]:
                    self._remove_backup(backup["path"])
        
        except Exception as e:
            self.logger.error(f"Backup cleanup failed: {e}")

    def _get_backup_list(self) -> List[Dict]:
        """Get list of all backups."""
        backups = []
        
        for filename in os.listdir(self.config.backup_dir):
            if filename.endswith(f".{self.config.backup_compression}"):
                backup_path = os.path.join(self.config.backup_dir, filename)
                backup_info = self._get_backup_info(backup_path)
                if backup_info:
                    backups.append(backup_info)
        
        return backups

    def _get_backup_info(self, backup_path: str) -> Optional[Dict]:
        """Get information about a backup."""
        try:
            # Extract metadata from backup
            metadata = self._extract_backup_metadata(backup_path)
            if not metadata:
                return None
            
            return {
                "path": backup_path,
                "timestamp": metadata["timestamp"],
                "backup_type": metadata["backup_type"],
                "size": os.path.getsize(backup_path),
                "compression": metadata["compression"]
            }
        
        except Exception as e:
            self.logger.error(f"Error getting backup info: {e}")
            return None

    def _extract_backup_metadata(self, backup_path: str) -> Optional[Dict]:
        """Extract metadata from a backup."""
        try:
            if self.config.backup_compression == "zip":
                with zipfile.ZipFile(backup_path, "r") as zip_file:
                    if "backup_metadata.json" in zip_file.namelist():
                        metadata_str = zip_file.read("backup_metadata.json")
                        return json.loads(metadata_str)
            
            elif self.config.backup_compression == "tar.gz":
                with tarfile.open(backup_path, "r:gz") as tar_file:
                    if "backup_metadata.json" in tar_file.getnames():
                        metadata_file = tar_file.extractfile("backup_metadata.json")
                        metadata_str = metadata_file.read()
                        return json.loads(metadata_str)
            
            return None
        
        except Exception as e:
            self.logger.error(f"Error extracting backup metadata: {e}")
            return None

    def _remove_backup(self, backup_path: str):
        """Remove a backup file."""
        try:
            os.remove(backup_path)
            self.logger.info(f"Removed backup: {backup_path}")
        except Exception as e:
            self.logger.error(f"Error removing backup: {e}")

    def _load_backup_metadata(self) -> Dict:
        """Load backup metadata from file."""
        metadata_path = os.path.join(
            self.config.backup_dir,
            "backup_metadata.json"
        )
        
        if os.path.exists(metadata_path):
            try:
                with open(metadata_path, "r") as f:
                    return json.load(f)
            except Exception as e:
                self.logger.error(f"Error loading backup metadata: {e}")
        
        return {}

    def _update_backup_metadata(self, backup_path: str):
        """Update backup metadata file."""
        try:
            # Get backup info
            backup_info = self._get_backup_info(backup_path)
            if not backup_info:
                return
            
            # Update metadata
            self.backup_metadata[backup_path] = backup_info
            
            # Save metadata
            metadata_path = os.path.join(
                self.config.backup_dir,
                "backup_metadata.json"
            )
            with open(metadata_path, "w") as f:
                json.dump(self.backup_metadata, f, indent=2)
        
        except Exception as e:
            self.logger.error(f"Error updating backup metadata: {e}")

    def _get_last_backup_timestamp(self) -> Optional[datetime]:
        """Get timestamp of the last backup."""
        backups = self._get_backup_list()
        if not backups:
            return None
        
        # Sort backups by timestamp
        backups.sort(key=lambda x: x["timestamp"], reverse=True)
        
        # Return timestamp of most recent backup
        return datetime.fromisoformat(backups[0]["timestamp"])

    def get_backup_status(self) -> Dict:
        """Get the current status of the backup system."""
        return {
            "backup_dir": self.config.backup_dir,
            "retention_days": self.config.retention_days,
            "max_backups": self.config.max_backups,
            "compression": {
                "type": self.config.backup_compression,
                "level": self.config.backup_compression_level
            },
            "backup_stats": {
                "total_backups": len(self._get_backup_list()),
                "total_size": self._get_total_backup_size(),
                "last_backup": self._get_last_backup_timestamp().isoformat()
                if self._get_last_backup_timestamp()
                else None
            },
            "settings": {
                "incremental_backups": self.config.incremental_backups,
                "verify_backups": self.config.verify_backups,
                "encrypt_backups": self.config.encrypt_backups,
                "parallel_backups": self.config.parallel_backups
            }
        }

    def _get_total_backup_size(self) -> int:
        """Get total size of all backups."""
        total_size = 0
        for backup in self._get_backup_list():
            total_size += backup["size"]
        return total_size

    def validate_backup_config(self) -> Tuple[bool, List[str]]:
        """Validate the backup configuration."""
        issues = []
        
        # Check backup directory
        if not os.path.exists(self.config.backup_dir):
            try:
                os.makedirs(self.config.backup_dir)
            except Exception as e:
                issues.append(f"Failed to create backup directory: {e}")
        
        # Check retention days
        if self.config.retention_days < 1:
            issues.append("Retention days must be at least 1")
        
        # Check max backups
        if self.config.max_backups < 1:
            issues.append("Max backups must be at least 1")
        
        # Check compression level
        if not 0 <= self.config.backup_compression_level <= 9:
            issues.append("Compression level must be between 0 and 9")
        
        # Check backup interval
        if self.config.backup_interval_hours < 1:
            issues.append("Backup interval must be at least 1 hour")
        
        return len(issues) == 0, issues 