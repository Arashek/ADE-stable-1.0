import os
import sys
import shutil
import logging
import hashlib
import mimetypes
from pathlib import Path
from typing import List, Dict, Optional, Union, Tuple
from datetime import datetime
import chardet
import git
from git.exc import GitCommandError
import aiofiles
import asyncio
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import platform
import re
from urllib.parse import urlparse

from src.core.config import settings
from src.core.models.repository import Repository
from src.core.models.file import FileInfo
from src.core.exceptions import (
    FileSystemError,
    RepositoryError,
    AuthenticationError,
    PermissionError
)

logger = logging.getLogger(__name__)

class FileSystemManager:
    def __init__(self, base_path: Optional[str] = None):
        self.base_path = Path(base_path or settings.REPOSITORY_BASE_PATH)
        self.base_path.mkdir(parents=True, exist_ok=True)
        self.observers: Dict[str, Observer] = {}
        self._setup_mime_types()

    def _setup_mime_types(self):
        """Add custom MIME types for common development files."""
        mimetypes.add_type('text/x-python', '.py')
        mimetypes.add_type('text/x-javascript', '.js')
        mimetypes.add_type('text/x-java', '.java')
        mimetypes.add_type('text/x-c++', '.cpp')
        mimetypes.add_type('text/x-c++', '.hpp')
        mimetypes.add_type('text/x-c', '.c')
        mimetypes.add_type('text/x-c', '.h')
        mimetypes.add_type('text/x-ruby', '.rb')
        mimetypes.add_type('text/x-php', '.php')
        mimetypes.add_type('text/x-go', '.go')
        mimetypes.add_type('text/x-rust', '.rs')
        mimetypes.add_type('text/x-swift', '.swift')
        mimetypes.add_type('text/x-kotlin', '.kt')
        mimetypes.add_type('text/x-scala', '.scala')
        mimetypes.add_type('text/x-typescript', '.ts')
        mimetypes.add_type('text/x-json', '.json')
        mimetypes.add_type('text/x-yaml', '.yaml')
        mimetypes.add_type('text/x-yaml', '.yml')
        mimetypes.add_type('text/x-toml', '.toml')
        mimetypes.add_type('text/x-markdown', '.md')
        mimetypes.add_type('text/x-dockerfile', '.dockerfile')
        mimetypes.add_type('text/x-shellscript', '.sh')
        mimetypes.add_type('text/x-shellscript', '.bash')

    async def clone_repository(
        self,
        url: str,
        branch: Optional[str] = None,
        auth_token: Optional[str] = None
    ) -> Repository:
        """
        Clone a repository from a URL with optional authentication.
        """
        try:
            # Parse repository URL
            parsed_url = urlparse(url)
            repo_name = os.path.basename(parsed_url.path).replace('.git', '')
            repo_path = self.base_path / repo_name

            # Configure Git credentials if provided
            git_config = {}
            if auth_token:
                if 'github.com' in parsed_url.netloc:
                    git_config['url'] = f"https://{auth_token}@github.com/"
                elif 'gitlab.com' in parsed_url.netloc:
                    git_config['url'] = f"https://oauth2:{auth_token}@gitlab.com/"

            # Clone repository
            try:
                repo = git.Repo.clone_from(
                    url,
                    repo_path,
                    branch=branch,
                    config=git_config
                )
            except GitCommandError as e:
                if 'Authentication failed' in str(e):
                    raise AuthenticationError("Failed to authenticate with repository")
                raise RepositoryError(f"Failed to clone repository: {str(e)}")

            # Create repository record
            repository = Repository(
                id=str(repo_path),
                name=repo_name,
                url=url,
                local_path=str(repo_path),
                branch=branch or repo.active_branch.name,
                last_updated=datetime.utcnow()
            )

            # Index repository files
            await self.index_repository(repository)

            logger.info(f"Successfully cloned repository: {repo_name}")
            return repository

        except Exception as e:
            logger.error(f"Error cloning repository {url}: {str(e)}")
            raise RepositoryError(f"Failed to clone repository: {str(e)}")

    async def index_repository(self, repository: Repository) -> List[FileInfo]:
        """
        Scan and index all files in a repository.
        """
        try:
            repo_path = Path(repository.local_path)
            files = []

            for root, _, filenames in os.walk(repo_path):
                for filename in filenames:
                    file_path = Path(root) / filename
                    relative_path = file_path.relative_to(repo_path)
                    
                    # Skip .git directory and other hidden files
                    if relative_path.parts[0] == '.git' or filename.startswith('.'):
                        continue

                    file_info = await self.get_file_info(file_path)
                    files.append(file_info)

            repository.files = files
            repository.file_count = len(files)
            repository.last_indexed = datetime.utcnow()

            return files

        except Exception as e:
            logger.error(f"Error indexing repository {repository.name}: {str(e)}")
            raise FileSystemError(f"Failed to index repository: {str(e)}")

    async def get_file_info(self, file_path: Path) -> FileInfo:
        """
        Get detailed information about a file.
        """
        try:
            stat = file_path.stat()
            mime_type, _ = mimetypes.guess_type(str(file_path))
            
            # Read file content to detect encoding
            async with aiofiles.open(file_path, 'rb') as f:
                content = await f.read()
                encoding = chardet.detect(content)['encoding']

            return FileInfo(
                path=str(file_path),
                name=file_path.name,
                size=stat.st_size,
                mime_type=mime_type or 'application/octet-stream',
                encoding=encoding or 'utf-8',
                created_at=datetime.fromtimestamp(stat.st_ctime),
                modified_at=datetime.fromtimestamp(stat.st_mtime),
                accessed_at=datetime.fromtimestamp(stat.st_atime),
                is_binary=not mime_type or not mime_type.startswith('text/'),
                hash=self._calculate_file_hash(content)
            )

        except Exception as e:
            logger.error(f"Error getting file info for {file_path}: {str(e)}")
            raise FileSystemError(f"Failed to get file info: {str(e)}")

    def _calculate_file_hash(self, content: bytes) -> str:
        """Calculate SHA-256 hash of file content."""
        return hashlib.sha256(content).hexdigest()

    async def read_file(
        self,
        file_path: Union[str, Path],
        encoding: Optional[str] = None
    ) -> str:
        """
        Read file content with proper encoding detection.
        """
        try:
            file_path = Path(file_path)
            if not file_path.exists():
                raise FileSystemError(f"File not found: {file_path}")

            # Read file content
            async with aiofiles.open(file_path, 'rb') as f:
                content = await f.read()

            # Detect encoding if not specified
            if not encoding:
                encoding = chardet.detect(content)['encoding'] or 'utf-8'

            # Decode content
            try:
                return content.decode(encoding)
            except UnicodeDecodeError:
                # Fallback to utf-8 if specified encoding fails
                return content.decode('utf-8', errors='replace')

        except Exception as e:
            logger.error(f"Error reading file {file_path}: {str(e)}")
            raise FileSystemError(f"Failed to read file: {str(e)}")

    async def write_file(
        self,
        file_path: Union[str, Path],
        content: str,
        encoding: str = 'utf-8'
    ) -> None:
        """
        Write content to a file with specified encoding.
        """
        try:
            file_path = Path(file_path)
            
            # Create parent directories if they don't exist
            file_path.parent.mkdir(parents=True, exist_ok=True)

            # Write content
            async with aiofiles.open(file_path, 'w', encoding=encoding) as f:
                await f.write(content)

        except Exception as e:
            logger.error(f"Error writing file {file_path}: {str(e)}")
            raise FileSystemError(f"Failed to write file: {str(e)}")

    async def delete_file(self, file_path: Union[str, Path]) -> None:
        """
        Delete a file.
        """
        try:
            file_path = Path(file_path)
            if not file_path.exists():
                raise FileSystemError(f"File not found: {file_path}")

            file_path.unlink()

        except Exception as e:
            logger.error(f"Error deleting file {file_path}: {str(e)}")
            raise FileSystemError(f"Failed to delete file: {str(e)}")

    async def create_directory(
        self,
        dir_path: Union[str, Path],
        exist_ok: bool = True
    ) -> None:
        """
        Create a directory and its parent directories.
        """
        try:
            dir_path = Path(dir_path)
            dir_path.mkdir(parents=True, exist_ok=exist_ok)

        except Exception as e:
            logger.error(f"Error creating directory {dir_path}: {str(e)}")
            raise FileSystemError(f"Failed to create directory: {str(e)}")

    async def delete_directory(
        self,
        dir_path: Union[str, Path],
        recursive: bool = True
    ) -> None:
        """
        Delete a directory and its contents.
        """
        try:
            dir_path = Path(dir_path)
            if not dir_path.exists():
                raise FileSystemError(f"Directory not found: {dir_path}")

            if recursive:
                shutil.rmtree(dir_path)
            else:
                dir_path.rmdir()

        except Exception as e:
            logger.error(f"Error deleting directory {dir_path}: {str(e)}")
            raise FileSystemError(f"Failed to delete directory: {str(e)}")

    def start_file_monitoring(
        self,
        path: Union[str, Path],
        callback: callable
    ) -> None:
        """
        Start monitoring a directory for file changes.
        """
        try:
            path = Path(path)
            if not path.exists():
                raise FileSystemError(f"Path not found: {path}")

            # Create event handler
            event_handler = FileChangeHandler(callback)
            
            # Create and start observer
            observer = Observer()
            observer.schedule(event_handler, str(path), recursive=True)
            observer.start()

            # Store observer reference
            self.observers[str(path)] = observer

            logger.info(f"Started monitoring directory: {path}")

        except Exception as e:
            logger.error(f"Error starting file monitoring for {path}: {str(e)}")
            raise FileSystemError(f"Failed to start file monitoring: {str(e)}")

    def stop_file_monitoring(self, path: Union[str, Path]) -> None:
        """
        Stop monitoring a directory for file changes.
        """
        try:
            path = str(path)
            if path in self.observers:
                observer = self.observers[path]
                observer.stop()
                observer.join()
                del self.observers[path]
                logger.info(f"Stopped monitoring directory: {path}")

        except Exception as e:
            logger.error(f"Error stopping file monitoring for {path}: {str(e)}")
            raise FileSystemError(f"Failed to stop file monitoring: {str(e)}")

    def normalize_path(self, path: Union[str, Path]) -> Path:
        """
        Normalize a path for the current operating system.
        """
        try:
            path = Path(path)
            if platform.system() == 'Windows':
                # Convert forward slashes to backslashes on Windows
                return Path(str(path).replace('/', '\\'))
            return path

        except Exception as e:
            logger.error(f"Error normalizing path {path}: {str(e)}")
            raise FileSystemError(f"Failed to normalize path: {str(e)}")

    def is_safe_path(self, base_path: Path, path: Path) -> bool:
        """
        Check if a path is safe to access (within base directory).
        """
        try:
            # Resolve both paths to handle symlinks
            base_path = base_path.resolve()
            path = path.resolve()
            
            # Check if path is within base directory
            return str(path).startswith(str(base_path))

        except Exception as e:
            logger.error(f"Error checking path safety: {str(e)}")
            return False

    async def search_files(
        self,
        directory: Union[str, Path],
        pattern: str,
        file_types: Optional[List[str]] = None
    ) -> List[FileInfo]:
        """
        Search for files matching a pattern.
        """
        try:
            directory = Path(directory)
            if not directory.exists():
                raise FileSystemError(f"Directory not found: {directory}")

            results = []
            regex = re.compile(pattern, re.IGNORECASE)

            for root, _, filenames in os.walk(directory):
                for filename in filenames:
                    # Skip hidden files
                    if filename.startswith('.'):
                        continue

                    # Check file type if specified
                    if file_types:
                        mime_type, _ = mimetypes.guess_type(filename)
                        if not mime_type or mime_type not in file_types:
                            continue

                    if regex.search(filename):
                        file_path = Path(root) / filename
                        file_info = await self.get_file_info(file_path)
                        results.append(file_info)

            return results

        except Exception as e:
            logger.error(f"Error searching files in {directory}: {str(e)}")
            raise FileSystemError(f"Failed to search files: {str(e)}")

class FileChangeHandler(FileSystemEventHandler):
    def __init__(self, callback: callable):
        self.callback = callback

    def on_created(self, event):
        if not event.is_directory:
            self.callback('created', event.src_path)

    def on_modified(self, event):
        if not event.is_directory:
            self.callback('modified', event.src_path)

    def on_deleted(self, event):
        if not event.is_directory:
            self.callback('deleted', event.src_path)

    def on_moved(self, event):
        if not event.is_directory:
            self.callback('moved', event.src_path, event.dest_path) 