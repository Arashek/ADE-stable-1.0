import os
import mimetypes
import hashlib
from typing import Optional, List, Dict, Tuple
from datetime import datetime
from pathlib import Path

def get_file_info(file_path: str) -> Dict:
    """Get detailed information about a file.
    
    Args:
        file_path: Path to the file
        
    Returns:
        Dictionary containing file information
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
        
    stat = path.stat()
    content_type, _ = mimetypes.guess_type(str(path))
    is_binary = content_type is None or not content_type.startswith('text/')
    
    info = {
        'path': str(path),
        'name': path.name,
        'extension': path.suffix.lower(),
        'size': stat.st_size,
        'last_modified': datetime.fromtimestamp(stat.st_mtime),
        'content_type': content_type or 'application/octet-stream',
        'is_binary': is_binary
    }
    
    if not is_binary:
        try:
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
                info['encoding'] = 'utf-8'
                info['line_count'] = len(content.splitlines())
        except UnicodeDecodeError:
            info['is_binary'] = True
            
    return info

def calculate_file_hash(file_path: str, chunk_size: int = 8192) -> str:
    """Calculate SHA-256 hash of a file.
    
    Args:
        file_path: Path to the file
        chunk_size: Size of chunks to read
        
    Returns:
        SHA-256 hash of the file
    """
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(chunk_size), b""):
            sha256_hash.update(chunk)
    return sha256_hash.hexdigest()

def is_text_file(file_path: str) -> bool:
    """Check if a file is a text file.
    
    Args:
        file_path: Path to the file
        
    Returns:
        True if the file is a text file
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            f.read(1024)
        return True
    except (UnicodeDecodeError, IOError):
        return False

def get_file_encoding(file_path: str) -> Optional[str]:
    """Detect file encoding.
    
    Args:
        file_path: Path to the file
        
    Returns:
        Detected encoding or None if binary
    """
    if not is_text_file(file_path):
        return None
        
    encodings = ['utf-8', 'ascii', 'iso-8859-1', 'cp1252']
    for encoding in encodings:
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                f.read()
            return encoding
        except UnicodeDecodeError:
            continue
    return None

def get_file_line_count(file_path: str) -> Optional[int]:
    """Get number of lines in a text file.
    
    Args:
        file_path: Path to the file
        
    Returns:
        Number of lines or None if binary
    """
    if not is_text_file(file_path):
        return None
        
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return sum(1 for _ in f)
    except (UnicodeDecodeError, IOError):
        return None

def get_directory_size(directory: str) -> int:
    """Calculate total size of a directory.
    
    Args:
        directory: Path to the directory
        
    Returns:
        Total size in bytes
    """
    total_size = 0
    for dirpath, _, filenames in os.walk(directory):
        for filename in filenames:
            file_path = os.path.join(dirpath, filename)
            total_size += os.path.getsize(file_path)
    return total_size

def get_file_permissions(file_path: str) -> Dict:
    """Get file permissions in a readable format.
    
    Args:
        file_path: Path to the file
        
    Returns:
        Dictionary containing permission information
    """
    stat = os.stat(file_path)
    mode = stat.st_mode
    
    def get_permission_string(mode: int) -> str:
        perms = ['r', 'w', 'x']
        return ''.join(p if mode & (1 << i) else '-' for i, p in enumerate(perms[::-1]))
    
    return {
        'owner_read': bool(mode & 0o400),
        'owner_write': bool(mode & 0o200),
        'owner_execute': bool(mode & 0o100),
        'group_read': bool(mode & 0o040),
        'group_write': bool(mode & 0o020),
        'group_execute': bool(mode & 0o010),
        'others_read': bool(mode & 0o004),
        'others_write': bool(mode & 0o002),
        'others_execute': bool(mode & 0o001),
        'permission_string': f"{get_permission_string(mode >> 6)}{get_permission_string(mode >> 3)}{get_permission_string(mode)}"
    }

def get_file_metadata(file_path: str) -> Dict:
    """Get comprehensive file metadata.
    
    Args:
        file_path: Path to the file
        
    Returns:
        Dictionary containing all file metadata
    """
    info = get_file_info(file_path)
    info.update({
        'hash': calculate_file_hash(file_path),
        'encoding': get_file_encoding(file_path),
        'line_count': get_file_line_count(file_path),
        'permissions': get_file_permissions(file_path)
    })
    return info 