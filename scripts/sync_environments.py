#!/usr/bin/env python3
import os
import shutil
import subprocess
import sys
from pathlib import Path
import logging
from typing import Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class EnvironmentSync:
    def __init__(self, source_env: str, target_env: str):
        self.source_env = source_env
        self.target_env = target_env
        self.project_root = Path(__file__).parent.parent
        self.source_path = self.project_root / 'environments' / source_env
        self.target_path = self.project_root / 'environments' / target_env

    def validate_environment(self, env_path: Path) -> bool:
        """Validate that the environment directory exists and has required files."""
        required_files = ['.env', 'docker-compose.yml']
        for file in required_files:
            if not (env_path / file).exists():
                logger.error(f"Missing required file {file} in {env_path}")
                return False
        return True

    def backup_target(self) -> bool:
        """Create a backup of the target environment."""
        backup_path = self.target_path.with_suffix('.backup')
        try:
            if self.target_path.exists():
                shutil.copytree(self.target_path, backup_path, dirs_exist_ok=True)
                logger.info(f"Created backup at {backup_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to create backup: {e}")
            return False

    def sync_files(self) -> bool:
        """Synchronize files from source to target environment."""
        try:
            # Copy docker-compose.yml
            shutil.copy2(
                self.source_path / 'docker-compose.yml',
                self.target_path / 'docker-compose.yml'
            )
            
            # Copy .env file, preserving sensitive values
            self._sync_env_file()
            
            logger.info(f"Successfully synchronized files from {self.source_env} to {self.target_env}")
            return True
        except Exception as e:
            logger.error(f"Failed to sync files: {e}")
            return False

    def _sync_env_file(self):
        """Synchronize .env file while preserving sensitive values."""
        source_env = self.source_path / '.env'
        target_env = self.target_path / '.env'
        
        if not source_env.exists():
            raise FileNotFoundError(f"Source .env file not found at {source_env}")
        
        # Read source and target env files
        with open(source_env, 'r') as f:
            source_lines = f.readlines()
        
        target_lines = []
        if target_env.exists():
            with open(target_env, 'r') as f:
                target_lines = f.readlines()
        
        # Create a map of existing target environment variables
        target_vars = {}
        for line in target_lines:
            if '=' in line:
                key = line.split('=')[0].strip()
                target_vars[key] = line.strip()
        
        # Merge environment variables
        new_lines = []
        for line in source_lines:
            if '=' in line:
                key = line.split('=')[0].strip()
                if key in target_vars:
                    # Preserve target value if it exists
                    new_lines.append(target_vars[key] + '\n')
                else:
                    new_lines.append(line)
            else:
                new_lines.append(line)
        
        # Write merged environment file
        with open(target_env, 'w') as f:
            f.writelines(new_lines)

    def validate_sync(self) -> bool:
        """Validate the synchronization result."""
        try:
            # Check if required files exist
            if not self.validate_environment(self.target_path):
                return False
            
            # Run docker-compose config to validate configuration
            result = subprocess.run(
                ['docker-compose', '-f', str(self.target_path / 'docker-compose.yml'), 'config'],
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                logger.error(f"Docker Compose validation failed: {result.stderr}")
                return False
            
            return True
        except Exception as e:
            logger.error(f"Validation failed: {e}")
            return False

    def sync(self) -> bool:
        """Perform the complete synchronization process."""
        logger.info(f"Starting synchronization from {self.source_env} to {self.target_env}")
        
        # Validate source environment
        if not self.validate_environment(self.source_path):
            logger.error("Source environment validation failed")
            return False
        
        # Create backup
        if not self.backup_target():
            logger.error("Backup creation failed")
            return False
        
        # Ensure target directory exists
        self.target_path.mkdir(parents=True, exist_ok=True)
        
        # Sync files
        if not self.sync_files():
            logger.error("File synchronization failed")
            return False
        
        # Validate sync
        if not self.validate_sync():
            logger.error("Sync validation failed")
            return False
        
        logger.info("Synchronization completed successfully")
        return True

def main():
    if len(sys.argv) != 3:
        print("Usage: python sync_environments.py <source_env> <target_env>")
        print("Example: python sync_environments.py development testing")
        sys.exit(1)
    
    source_env = sys.argv[1]
    target_env = sys.argv[2]
    
    sync = EnvironmentSync(source_env, target_env)
    if not sync.sync():
        sys.exit(1)

if __name__ == "__main__":
    main() 