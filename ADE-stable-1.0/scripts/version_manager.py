#!/usr/bin/env python3
import os
import sys
import subprocess
import json
from datetime import datetime
from pathlib import Path
import logging
from typing import Optional, Tuple

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class VersionManager:
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.changelog_path = self.project_root / 'CHANGELOG.md'
        self.version_file = self.project_root / 'VERSION'
        self.current_version = self._read_version()

    def _read_version(self) -> str:
        """Read the current version from VERSION file."""
        if self.version_file.exists():
            with open(self.version_file, 'r') as f:
                return f.read().strip()
        return '0.1.0'

    def _write_version(self, version: str):
        """Write the version to VERSION file."""
        with open(self.version_file, 'w') as f:
            f.write(version)

    def _parse_version(self, version: str) -> Tuple[int, int, int]:
        """Parse version string into major, minor, patch components."""
        major, minor, patch = map(int, version.split('.'))
        return major, minor, patch

    def _format_version(self, major: int, minor: int, patch: int) -> str:
        """Format version components into version string."""
        return f"{major}.{minor}.{patch}"

    def bump_version(self, bump_type: str) -> str:
        """Bump the version number based on the specified type."""
        major, minor, patch = self._parse_version(self.current_version)
        
        if bump_type == 'major':
            major += 1
            minor = 0
            patch = 0
        elif bump_type == 'minor':
            minor += 1
            patch = 0
        elif bump_type == 'patch':
            patch += 1
        else:
            raise ValueError(f"Invalid bump type: {bump_type}")
        
        new_version = self._format_version(major, minor, patch)
        self._write_version(new_version)
        self.current_version = new_version
        return new_version

    def create_changelog_entry(self, version: str, changes: list):
        """Create a new changelog entry."""
        if not self.changelog_path.exists():
            with open(self.changelog_path, 'w') as f:
                f.write("# Changelog\n\n")
        
        with open(self.changelog_path, 'r') as f:
            content = f.read()
        
        # Create new entry
        date = datetime.now().strftime('%Y-%m-%d')
        entry = f"\n## [{version}] - {date}\n\n"
        
        # Add changes
        for change in changes:
            entry += f"- {change}\n"
        
        # Insert new entry after the header
        header_end = content.find('\n\n') + 2
        new_content = content[:header_end] + entry + content[header_end:]
        
        with open(self.changelog_path, 'w') as f:
            f.write(new_content)

    def create_git_tag(self, version: str):
        """Create a Git tag for the version."""
        try:
            subprocess.run(['git', 'tag', f'v{version}'], check=True)
            subprocess.run(['git', 'push', 'origin', f'v{version}'], check=True)
            logger.info(f"Created and pushed Git tag v{version}")
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to create Git tag: {e}")
            raise

    def rollback_version(self, version: str):
        """Rollback to a specific version."""
        try:
            # Verify the version exists in Git history
            subprocess.run(['git', 'show', f'v{version}'], check=True, capture_output=True)
            
            # Reset to the version
            subprocess.run(['git', 'reset', '--hard', f'v{version}'], check=True)
            self._write_version(version)
            self.current_version = version
            
            logger.info(f"Successfully rolled back to version {version}")
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to rollback version: {e}")
            raise

    def release(self, bump_type: str, changes: list):
        """Create a new release with version bump and changelog entry."""
        try:
            # Bump version
            new_version = self.bump_version(bump_type)
            
            # Create changelog entry
            self.create_changelog_entry(new_version, changes)
            
            # Commit changes
            subprocess.run(['git', 'add', str(self.version_file), str(self.changelog_path)], check=True)
            subprocess.run(['git', 'commit', '-m', f'Release v{new_version}'], check=True)
            
            # Create and push Git tag
            self.create_git_tag(new_version)
            
            logger.info(f"Successfully created release v{new_version}")
            return new_version
        except Exception as e:
            logger.error(f"Failed to create release: {e}")
            raise

def main():
    if len(sys.argv) < 3:
        print("Usage: python version_manager.py <command> [arguments]")
        print("Commands:")
        print("  bump <major|minor|patch>")
        print("  release <major|minor|patch> <change1> [change2 ...]")
        print("  rollback <version>")
        sys.exit(1)
    
    manager = VersionManager()
    command = sys.argv[1]
    
    try:
        if command == 'bump':
            if len(sys.argv) != 3:
                print("Usage: python version_manager.py bump <major|minor|patch>")
                sys.exit(1)
            new_version = manager.bump_version(sys.argv[2])
            print(f"Version bumped to {new_version}")
        
        elif command == 'release':
            if len(sys.argv) < 4:
                print("Usage: python version_manager.py release <major|minor|patch> <change1> [change2 ...]")
                sys.exit(1)
            bump_type = sys.argv[2]
            changes = sys.argv[3:]
            new_version = manager.release(bump_type, changes)
            print(f"Created release v{new_version}")
        
        elif command == 'rollback':
            if len(sys.argv) != 3:
                print("Usage: python version_manager.py rollback <version>")
                sys.exit(1)
            manager.rollback_version(sys.argv[2])
            print(f"Rolled back to version {sys.argv[2]}")
        
        else:
            print(f"Unknown command: {command}")
            sys.exit(1)
    
    except Exception as e:
        logger.error(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 