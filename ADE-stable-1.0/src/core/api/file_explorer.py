from fastapi import APIRouter, HTTPException, Depends, Query, Path, UploadFile, File, Form, WebSocket, Body
from fastapi.responses import JSONResponse, StreamingResponse, FileResponse
from typing import List, Optional, Dict, Any, Set, Union, Enum
from datetime import datetime
import os
import mimetypes
import chardet
import magic
from pathlib import Path
import shutil
import asyncio
from concurrent.futures import ThreadPoolExecutor
import re
from pydantic import BaseModel, Field
import logging
import zipfile
import io
import hashlib
import json
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import py7zr
import rarfile
import tarfile
import gzip
import bz2
import lzma
import csv
import pandas as pd
import openpyxl
import sqlite3
import psycopg2
import mysql.connector
from PIL import Image
import mutagen
import cv2
import numpy as np
from ..security.auth import get_current_user
from ..models.user import User

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

# Constants
CHUNK_SIZE = 1024 * 1024  # 1MB chunks
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB
ALLOWED_EXTENSIONS = {
    # Text files
    '.txt', '.md', '.rst', '.csv', '.json', '.yaml', '.yml', '.xml', '.html', '.css',
    # Code files
    '.py', '.js', '.ts', '.java', '.cpp', '.c', '.h', '.cs', '.go', '.rs', '.rb', '.php',
    '.swift', '.kt', '.scala', '.r', '.matlab', '.sql', '.sh', '.bat', '.ps1',
    # Configuration files
    '.ini', '.cfg', '.conf', '.env', '.properties', '.toml', '.xml', '.yaml', '.yml',
    # Documentation
    '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx', '.odt', '.ods', '.odp',
    # Images
    '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.webp', '.ico',
    # Audio
    '.mp3', '.wav', '.ogg', '.flac', '.m4a',
    # Video
    '.mp4', '.avi', '.mov', '.wmv', '.flv', '.webm',
    # Archives
    '.zip', '.rar', '.7z', '.tar', '.gz', '.bz2',
    # Data files
    '.csv', '.xlsx', '.xls', '.db', '.sqlite', '.sqlite3',
    # Fonts
    '.ttf', '.otf', '.woff', '.woff2', '.eot',
    # 3D models
    '.obj', '.fbx', '.stl', '.3ds', '.dae',
    # CAD files
    '.dwg', '.dxf', '.step', '.stp', '.iges', '.igs',
    # Additional file types
    '.epub', '.mobi', '.azw3',  # E-books
    '.iso', '.img', '.bin',     # Disk images
    '.vmdk', '.vhd', '.vhdx',   # Virtual machine disks
    '.psd', '.ai', '.sketch',   # Design files
    '.dmg', '.app', '.exe',     # Executables
    '.msi', '.deb', '.rpm',     # Installers
    '.apk', '.ipa', '.aab',     # Mobile apps
    '.jar', '.war', '.ear',     # Java archives
    '.pyc', '.pyo', '.pyd',     # Python compiled
    '.class', '.o', '.obj',     # Compiled files
    '.dll', '.so', '.dylib',    # Libraries
    '.swf', '.fla', '.as',      # Flash files
    '.blend', '.ma', '.mb',     # 3D files
    '.max', '.3ds', '.fbx',     # 3D files
    '.maya', '.c4d', '.lwo',    # 3D files
    '.unity', '.unet', '.uasset', # Unity files
    '.skp', '.rvt', '.ifc',     # CAD files
    '.dwg', '.dxf', '.step',    # CAD files
    '.iges', '.igs', '.stp',    # CAD files
    '.x3d', '.vrml', '.obj',    # 3D web files
    '.glb', '.gltf', '.usdz',   # 3D web files
    '.svg', '.eps', '.ai',      # Vector graphics
    '.psd', '.xcf', '.kra',     # Image editing
    '.raw', '.cr2', '.nef',     # Raw images
    '.wav', '.aiff', '.flac',   # Audio formats
    '.mp3', '.aac', '.ogg',     # Audio formats
    '.m4a', '.wma', '.alac',    # Audio formats
    '.mp4', '.mov', '.avi',     # Video formats
    '.mkv', '.webm', '.flv',    # Video formats
    '.m4v', '.wmv', '.vob',     # Video formats
    '.pdf', '.epub', '.mobi',   # Documents
    '.doc', '.docx', '.odt',    # Documents
    '.xls', '.xlsx', '.ods',    # Spreadsheets
    '.ppt', '.pptx', '.odp',    # Presentations
    '.csv', '.tsv', '.json',    # Data files
    '.xml', '.yaml', '.toml',   # Data files
    '.db', '.sqlite', '.sqlite3', # Databases
    '.psql', '.mysql', '.mdb',  # Databases
    '.zip', '.rar', '.7z',      # Archives
    '.tar', '.gz', '.bz2',      # Archives
    '.xz', '.lzma', '.zst',     # Archives
}

# MIME type to language mapping
MIME_TO_LANGUAGE = {
    'text/x-python': 'python',
    'text/javascript': 'javascript',
    'application/typescript': 'typescript',
    'text/x-java': 'java',
    'text/x-c++': 'cpp',
    'text/x-c': 'c',
    'text/x-csharp': 'csharp',
    'text/x-go': 'go',
    'text/x-rust': 'rust',
    'text/x-ruby': 'ruby',
    'text/x-php': 'php',
    'text/html': 'html',
    'text/css': 'css',
    'application/json': 'json',
    'text/x-yaml': 'yaml',
    'text/markdown': 'markdown',
    'text/x-rst': 'restructuredtext',
    'text/x-swift': 'swift',
    'text/x-kotlin': 'kotlin',
    'text/x-scala': 'scala',
    'text/x-r': 'r',
    'text/x-matlab': 'matlab',
    'text/x-sql': 'sql',
    'text/x-shellscript': 'shell',
    'application/x-bat': 'batch',
    'application/x-powershell': 'powershell'
}

# WebSocket connections store
active_connections: Dict[str, Set[WebSocket]] = {}

class FileSystemEvent(BaseModel):
    event_type: str  # 'created', 'modified', 'deleted', 'moved'
    path: str
    is_directory: bool
    metadata: Optional[Dict[str, Any]] = None
    old_path: Optional[str] = None

class FileWatcher(FileSystemEventHandler):
    def __init__(self, base_path: Path):
        self.base_path = base_path
        self.observer = None

    def start(self):
        self.observer = Observer()
        self.observer.schedule(self, str(self.base_path), recursive=True)
        self.observer.start()

    def stop(self):
        if self.observer:
            self.observer.stop()
            self.observer.join()

    def on_created(self, event):
        if event.is_directory:
            self._notify_clients('created', event.src_path, True)
        else:
            self._notify_clients('created', event.src_path, False, self._get_metadata(event.src_path))

    def on_modified(self, event):
        if not event.is_directory:
            self._notify_clients('modified', event.src_path, False, self._get_metadata(event.src_path))

    def on_deleted(self, event):
        self._notify_clients('deleted', event.src_path, event.is_directory)

    def on_moved(self, event):
        self._notify_clients('moved', event.dest_path, event.is_directory, 
                           self._get_metadata(event.dest_path) if not event.is_directory else None,
                           event.src_path)

    def _get_metadata(self, path: str) -> Optional[Dict[str, Any]]:
        try:
            file_path = Path(path)
            if file_path.exists():
                return get_file_metadata(file_path)
        except Exception as e:
            logger.error(f"Error getting metadata for {path}: {str(e)}")
        return None

    def _notify_clients(self, event_type: str, path: str, is_directory: bool,
                       metadata: Optional[Dict[str, Any]] = None, old_path: Optional[str] = None):
        try:
            relative_path = str(Path(path).relative_to(self.base_path))
            event = FileSystemEvent(
                event_type=event_type,
                path=relative_path,
                is_directory=is_directory,
                metadata=metadata,
                old_path=old_path
            )
            
            # Notify all connected clients
            for connections in active_connections.values():
                for connection in connections:
                    asyncio.create_task(connection.send_json(event.dict()))
        except Exception as e:
            logger.error(f"Error notifying clients: {str(e)}")

# Global file watcher instance
file_watcher = None

def get_file_watcher() -> FileWatcher:
    global file_watcher
    if file_watcher is None:
        base_path = Path(os.getenv('ALLOWED_BASE_PATH', '/'))
        file_watcher = FileWatcher(base_path)
        file_watcher.start()
    return file_watcher

@router.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    """WebSocket endpoint for real-time file system updates."""
    await websocket.accept()
    
    if user_id not in active_connections:
        active_connections[user_id] = set()
    active_connections[user_id].add(websocket)
    
    try:
        while True:
            # Keep the connection alive and handle any client messages
            data = await websocket.receive_text()
            try:
                message = json.loads(data)
                # Handle any client-side messages here
                logger.info(f"Received message from {user_id}: {message}")
            except json.JSONDecodeError:
                logger.error(f"Invalid JSON from {user_id}")
    except Exception as e:
        logger.error(f"WebSocket error for {user_id}: {str(e)}")
    finally:
        active_connections[user_id].remove(websocket)
        if not active_connections[user_id]:
            del active_connections[user_id]

@router.on_event("startup")
async def startup_event():
    """Initialize file watcher on application startup."""
    get_file_watcher()

@router.on_event("shutdown")
async def shutdown_event():
    """Clean up file watcher on application shutdown."""
    global file_watcher
    if file_watcher:
        file_watcher.stop()
        file_watcher = None

class FileItem(BaseModel):
    name: str
    path: str
    type: str  # 'file' or 'directory'
    size: Optional[int] = None
    created_at: datetime
    modified_at: datetime
    mime_type: Optional[str] = None
    language: Optional[str] = None
    is_binary: bool = False
    hash: Optional[str] = None
    compression_ratio: Optional[float] = None

class FileContent(BaseModel):
    content: str
    encoding: str
    mime_type: str
    language: Optional[str] = None
    size: int
    modified_at: datetime
    hash: str
    compression_ratio: Optional[float] = None

class FileUpdate(BaseModel):
    path: str
    content: str
    encoding: Optional[str] = None

class DirectoryCreate(BaseModel):
    path: str
    name: str

class SearchQuery(BaseModel):
    pattern: str
    use_regex: bool = False
    file_types: Optional[List[str]] = None
    modified_after: Optional[datetime] = None
    modified_before: Optional[datetime] = None
    case_sensitive: bool = False
    min_size: Optional[int] = None
    max_size: Optional[int] = None
    content_type: Optional[str] = None
    language: Optional[str] = None
    hash: Optional[str] = None

class CompressionFormat(str, Enum):
    ZIP = "zip"
    SEVENZIP = "7z"
    RAR = "rar"
    TAR = "tar"
    TAR_GZ = "tar.gz"
    TAR_BZ2 = "tar.bz2"
    TAR_XZ = "tar.xz"
    GZ = "gz"
    BZ2 = "bz2"
    XZ = "xz"
    LZMA = "lzma"
    ZSTD = "zst"

class CompressionOptions(BaseModel):
    format: CompressionFormat = CompressionFormat.ZIP
    level: int = Field(default=6, ge=0, le=9, description="Compression level (0-9)")
    password: Optional[str] = None
    solid: bool = False  # For 7z format
    multi_volume: bool = False
    volume_size: Optional[int] = None  # Size in bytes for multi-volume archives

def compress_file_with_format(
    file_path: Path,
    output_path: Path,
    options: CompressionOptions
) -> Dict[str, Any]:
    """Compress a file using the specified format and options."""
    try:
        original_size = file_path.stat().st_size
        if original_size == 0:
            raise ValueError("Cannot compress empty file")

        if options.format == CompressionFormat.ZIP:
            with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zf:
                if options.password:
                    zf.setpassword(options.password.encode())
                zf.write(file_path, file_path.name)
        elif options.format == CompressionFormat.SEVENZIP:
            with py7zr.SevenZipFile(output_path, 'w', password=options.password) as sz:
                sz.write(file_path, file_path.name)
        elif options.format == CompressionFormat.RAR:
            with rarfile.RarFile(output_path, 'w') as rf:
                rf.write(file_path, file_path.name)
        elif options.format == CompressionFormat.TAR:
            with tarfile.open(output_path, 'w') as tf:
                tf.add(file_path, arcname=file_path.name)
        elif options.format in [CompressionFormat.TAR_GZ, CompressionFormat.TAR_BZ2, CompressionFormat.TAR_XZ]:
            mode = {
                CompressionFormat.TAR_GZ: 'w:gz',
                CompressionFormat.TAR_BZ2: 'w:bz2',
                CompressionFormat.TAR_XZ: 'w:xz'
            }[options.format]
            with tarfile.open(output_path, mode) as tf:
                tf.add(file_path, arcname=file_path.name)
        elif options.format == CompressionFormat.GZ:
            with gzip.open(output_path, 'wb', compresslevel=options.level) as gz:
                with open(file_path, 'rb') as f:
                    gz.write(f.read())
        elif options.format == CompressionFormat.BZ2:
            with bz2.open(output_path, 'wb', compresslevel=options.level) as bz:
                with open(file_path, 'rb') as f:
                    bz.write(f.read())
        elif options.format == CompressionFormat.XZ:
            with lzma.open(output_path, 'wb', preset=options.level) as xz:
                with open(file_path, 'rb') as f:
                    xz.write(f.read())
        else:
            raise ValueError(f"Unsupported compression format: {options.format}")

        compressed_size = output_path.stat().st_size
        return {
            'original_size': original_size,
            'compressed_size': compressed_size,
            'compression_ratio': 1 - (compressed_size / original_size)
        }
    except Exception as e:
        logger.error(f"Error compressing file: {str(e)}")
        raise

def decompress_file_with_format(
    file_path: Path,
    output_path: Path,
    options: CompressionOptions
) -> Dict[str, Any]:
    """Decompress a file using the specified format and options."""
    try:
        if not file_path.exists():
            raise FileNotFoundError(f"Archive not found: {file_path}")

        if options.format == CompressionFormat.ZIP:
            with zipfile.ZipFile(file_path, 'r') as zf:
                if options.password:
                    zf.setpassword(options.password.encode())
                zf.extractall(output_path)
        elif options.format == CompressionFormat.SEVENZIP:
            with py7zr.SevenZipFile(file_path, 'r', password=options.password) as sz:
                sz.extractall(output_path)
        elif options.format == CompressionFormat.RAR:
            with rarfile.RarFile(file_path, 'r') as rf:
                rf.extractall(output_path)
        elif options.format in [CompressionFormat.TAR, CompressionFormat.TAR_GZ, CompressionFormat.TAR_BZ2, CompressionFormat.TAR_XZ]:
            with tarfile.open(file_path, 'r:*') as tf:
                tf.extractall(output_path)
        elif options.format == CompressionFormat.GZ:
            with gzip.open(file_path, 'rb') as gz:
                with open(output_path, 'wb') as f:
                    f.write(gz.read())
        elif options.format == CompressionFormat.BZ2:
            with bz2.open(file_path, 'rb') as bz:
                with open(output_path, 'wb') as f:
                    f.write(bz.read())
        elif options.format == CompressionFormat.XZ:
            with lzma.open(file_path, 'rb') as xz:
                with open(output_path, 'wb') as f:
                    f.write(xz.read())
        else:
            raise ValueError(f"Unsupported compression format: {options.format}")

        return {'status': 'success', 'extracted_path': str(output_path)}
    except Exception as e:
        logger.error(f"Error decompressing file: {str(e)}")
        raise

@router.post("/compress")
async def compress_file(
    path: str = Query(..., description="File path to compress"),
    options: CompressionOptions = Body(...),
    current_user: User = Depends(get_current_user)
):
    """Compress a file using specified format and options."""
    try:
        file_path = validate_path(path)
        if not file_path.is_file():
            raise HTTPException(status_code=400, detail="Path is not a file")

        # Determine output path based on format
        output_path = file_path.with_suffix(f".{options.format}")
        
        # Handle multi-volume archives
        if options.multi_volume and options.volume_size:
            volume_size = options.volume_size
            total_size = file_path.stat().st_size
            num_volumes = (total_size + volume_size - 1) // volume_size
            
            results = []
            for i in range(num_volumes):
                start = i * volume_size
                end = min((i + 1) * volume_size, total_size)
                volume_path = output_path.with_suffix(f".{options.format}.{i+1:03d}")
                
                # Create temporary file for this volume
                with open(file_path, 'rb') as f:
                    f.seek(start)
                    volume_data = f.read(end - start)
                
                # Compress volume
                with open(volume_path, 'wb') as f:
                    if options.format == CompressionFormat.ZIP:
                        with zipfile.ZipFile(f, 'w', zipfile.ZIP_DEFLATED) as zf:
                            zf.writestr(file_path.name, volume_data)
                    # Add support for other formats...
                
                results.append({
                    'volume': i + 1,
                    'path': str(volume_path),
                    'size': volume_path.stat().st_size
                })
            
            return {
                'status': 'success',
                'total_volumes': num_volumes,
                'volumes': results
            }
        else:
            # Single file compression
            result = compress_file_with_format(file_path, output_path, options)
            return {
                'status': 'success',
                'compressed_path': str(output_path),
                **result
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/decompress")
async def decompress_file(
    path: str = Query(..., description="Compressed file path to decompress"),
    options: CompressionOptions = Body(...),
    current_user: User = Depends(get_current_user)
):
    """Decompress a file using specified format and options."""
    try:
        file_path = validate_path(path)
        if not file_path.is_file():
            raise HTTPException(status_code=400, detail="Path is not a file")

        # Handle multi-volume archives
        if options.multi_volume:
            # Find all volume files
            volume_pattern = re.compile(rf"{file_path.stem}\.{options.format}\.\d{{3}}$")
            volume_files = sorted(
                [f for f in file_path.parent.glob(f"{file_path.stem}.{options.format}.*")
                 if volume_pattern.match(f.name)],
                key=lambda x: int(x.suffix[1:])
            )
            
            if not volume_files:
                raise HTTPException(status_code=400, detail="No volume files found")
            
            # Create output directory
            output_dir = file_path.parent / file_path.stem
            output_dir.mkdir(exist_ok=True)
            
            # Decompress each volume
            for volume_file in volume_files:
                decompress_file_with_format(volume_file, output_dir, options)
            
            return {
                'status': 'success',
                'extracted_path': str(output_dir)
            }
        else:
            # Single file decompression
            output_path = file_path.parent / file_path.stem
            return decompress_file_with_format(file_path, output_path, options)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/list", response_model=List[FileItem])
async def list_files(
    path: str = Query(..., description="Directory path to list"),
    current_user: User = Depends(get_current_user)
):
    """List files and directories in the specified path."""
    try:
        dir_path = validate_path(path)
        if not dir_path.is_dir():
            raise HTTPException(status_code=400, detail="Path is not a directory")
            
        items = []
        for item in dir_path.iterdir():
            try:
                metadata = get_file_metadata(item)
                items.append(FileItem(
                    name=item.name,
                    path=str(item.relative_to(dir_path)),
                    type='directory' if item.is_dir() else 'file',
                    **metadata
                ))
            except Exception as e:
                logger.error(f"Error processing {item}: {str(e)}")
                continue
                
        return items
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/content", response_model=FileContent)
async def get_file_content(
    path: str = Query(..., description="File path to read"),
    current_user: User = Depends(get_current_user)
):
    """Get file content with proper encoding detection."""
    try:
        file_path = validate_path(path)
        if not file_path.is_file():
            raise HTTPException(status_code=400, detail="Path is not a file")
            
        if file_path.stat().st_size > MAX_FILE_SIZE:
            raise HTTPException(status_code=413, detail="File too large")
            
        metadata = get_file_metadata(file_path)
        if metadata['is_binary']:
            raise HTTPException(status_code=400, detail="Cannot read binary file")
            
        encoding = detect_encoding(file_path)
        with open(file_path, 'r', encoding=encoding) as f:
            content = f.read()
            
        return FileContent(
            content=content,
            encoding=encoding,
            **metadata
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/content")
async def update_file_content(
    update: FileUpdate,
    current_user: User = Depends(get_current_user)
):
    """Update file content with proper encoding handling."""
    try:
        file_path = validate_path(update.path)
        if not file_path.is_file():
            raise HTTPException(status_code=400, detail="Path is not a file")
            
        # Check for concurrent modifications
        current_mtime = file_path.stat().st_mtime
        if update.modified_at and update.modified_at.timestamp() < current_mtime:
            raise HTTPException(status_code=409, detail="File has been modified")
            
        encoding = update.encoding or detect_encoding(file_path)
        with open(file_path, 'w', encoding=encoding) as f:
            f.write(update.content)
            
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/directory")
async def create_directory(
    directory: DirectoryCreate,
    current_user: User = Depends(get_current_user)
):
    """Create a new directory."""
    try:
        parent_path = validate_path(directory.path)
        new_dir = parent_path / directory.name
        
        if new_dir.exists():
            raise HTTPException(status_code=400, detail="Directory already exists")
            
        new_dir.mkdir(parents=True)
        return {"status": "success", "path": str(new_dir)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/path")
async def delete_path(
    path: str = Query(..., description="Path to delete"),
    current_user: User = Depends(get_current_user)
):
    """Delete a file or directory."""
    try:
        target_path = validate_path(path)
        if not target_path.exists():
            raise HTTPException(status_code=404, detail="Path does not exist")
            
        if target_path.is_dir():
            shutil.rmtree(target_path)
        else:
            target_path.unlink()
            
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    path: str = Form(...),
    current_user: User = Depends(get_current_user)
):
    """Upload a file to the specified path."""
    try:
        target_path = validate_path(path) / file.filename
        
        # Check file size
        file_size = 0
        with open(target_path, 'wb') as f:
            while chunk := await file.read(CHUNK_SIZE):
                file_size += len(chunk)
                if file_size > MAX_FILE_SIZE:
                    raise HTTPException(status_code=413, detail="File too large")
                f.write(chunk)
        
        return {"status": "success", "path": str(target_path)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/download")
async def download_file(
    path: str = Query(..., description="File path to download"),
    compress: bool = Query(False, description="Compress file before download"),
    current_user: User = Depends(get_current_user)
):
    """Download a file, optionally compressed."""
    try:
        file_path = validate_path(path)
        if not file_path.is_file():
            raise HTTPException(status_code=400, detail="Path is not a file")
            
        if compress:
            # Create a temporary zip file in memory
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                zip_file.write(file_path, file_path.name)
            
            zip_buffer.seek(0)
            return StreamingResponse(
                zip_buffer,
                media_type='application/zip',
                headers={
                    'Content-Disposition': f'attachment; filename="{file_path.name}.zip"'
                }
            )
        else:
            return FileResponse(
                file_path,
                filename=file_path.name,
                media_type=detect_mime_type(file_path)
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/search")
async def search_files(
    query: SearchQuery,
    current_user: User = Depends(get_current_user)
):
    """Search files with various filters."""
    try:
        results = []
        base_path = Path(os.getenv('ALLOWED_BASE_PATH', '/'))
        
        def search_file(file_path: Path):
            try:
                if not file_path.is_file():
                    return
                    
                # Apply filters
                if query.file_types and file_path.suffix.lower() not in query.file_types:
                    return
                    
                stat = file_path.stat()
                if query.min_size and stat.st_size < query.min_size:
                    return
                if query.max_size and stat.st_size > query.max_size:
                    return
                    
                if query.modified_after and datetime.fromtimestamp(stat.st_mtime) < query.modified_after:
                    return
                if query.modified_before and datetime.fromtimestamp(stat.st_mtime) > query.modified_before:
                    return
                    
                metadata = get_file_metadata(file_path)
                if query.content_type and metadata['mime_type'] != query.content_type:
                    return
                if query.language and metadata['language'] != query.language:
                    return
                if query.hash and metadata['hash'] != query.hash:
                    return
                    
                # Skip binary files unless specifically searching for them
                if not query.content_type and not metadata['mime_type'].startswith('text/'):
                    return
                    
                # Read and search file content
                encoding = detect_encoding(file_path)
                with open(file_path, 'r', encoding=encoding) as f:
                    content = f.read()
                    
                pattern = query.pattern
                if not query.use_regex:
                    pattern = re.escape(pattern)
                    
                flags = 0 if query.case_sensitive else re.IGNORECASE
                matches = list(re.finditer(pattern, content, flags))
                
                if matches:
                    results.append({
                        'path': str(file_path.relative_to(base_path)),
                        'metadata': metadata,
                        'matches': [
                            {
                                'line': content[:m.start()].count('\n') + 1,
                                'position': m.start(),
                                'context': content[max(0, m.start()-50):min(len(content), m.end()+50)]
                            }
                            for m in matches
                        ]
                    })
            except Exception as e:
                logger.error(f"Error searching {file_path}: {str(e)}")
                
        # Use ThreadPoolExecutor for parallel file searching
        with ThreadPoolExecutor() as executor:
            futures = []
            for file_path in base_path.rglob('*'):
                futures.append(executor.submit(search_file, file_path))
                
            # Wait for all searches to complete
            for future in futures:
                future.result()
                
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 