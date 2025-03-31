import asyncio
from typing import Dict, Any, Optional
import logging
from pathlib import Path
import json
import os
from datetime import datetime

from ..services.ocr_service import OCRService
from ..services.voice_transcription import VoiceTranscriptionService
from ..services.image_analysis import ImageAnalysisService

class MediaRouter:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.ocr_service = OCRService()
        self.voice_service = VoiceTranscriptionService()
        self.image_service = ImageAnalysisService()
        
        # Initialize storage
        self.storage_dir = Path("storage")
        self.storage_dir.mkdir(exist_ok=True)
        
        # Initialize processing queue
        self.processing_queue = asyncio.Queue()
        self.processing_tasks = {}
        
        # Start processing worker
        asyncio.create_task(self._process_queue())
        
    async def update_status(self, media_id: str, status: str):
        """
        Update the processing status of a media file
        """
        try:
            status_file = self.storage_dir / f"{media_id}_status.json"
            status_data = {
                "status": status,
                "updated_at": datetime.utcnow().isoformat()
            }
            
            async with aiofiles.open(status_file, 'w') as f:
                await f.write(json.dumps(status_data))
                
        except Exception as e:
            self.logger.error(f"Failed to update status: {str(e)}")
            raise

    async def get_status(self, media_id: str) -> str:
        """
        Get the current processing status of a media file
        """
        try:
            status_file = self.storage_dir / f"{media_id}_status.json"
            if not status_file.exists():
                return "not_found"
                
            async with aiofiles.open(status_file, 'r') as f:
                status_data = json.loads(await f.read())
                return status_data.get("status", "unknown")
                
        except Exception as e:
            self.logger.error(f"Failed to get status: {str(e)}")
            return "error"

    async def store_result(self, media_id: str, result: Dict[str, Any]):
        """
        Store the processing results
        """
        try:
            result_file = self.storage_dir / f"{media_id}_result.json"
            result_data = {
                "result": result,
                "completed_at": datetime.utcnow().isoformat()
            }
            
            async with aiofiles.open(result_file, 'w') as f:
                await f.write(json.dumps(result_data))
                
        except Exception as e:
            self.logger.error(f"Failed to store result: {str(e)}")
            raise

    async def get_result(self, media_id: str) -> Optional[Dict[str, Any]]:
        """
        Get the processing results
        """
        try:
            result_file = self.storage_dir / f"{media_id}_result.json"
            if not result_file.exists():
                return None
                
            async with aiofiles.open(result_file, 'r') as f:
                result_data = json.loads(await f.read())
                return result_data.get("result")
                
        except Exception as e:
            self.logger.error(f"Failed to get result: {str(e)}")
            return None

    async def store_error(self, media_id: str, error: str):
        """
        Store processing error
        """
        try:
            error_file = self.storage_dir / f"{media_id}_error.json"
            error_data = {
                "error": error,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            async with aiofiles.open(error_file, 'w') as f:
                await f.write(json.dumps(error_data))
                
        except Exception as e:
            self.logger.error(f"Failed to store error: {str(e)}")
            raise

    async def get_error(self, media_id: str) -> Optional[str]:
        """
        Get processing error if any
        """
        try:
            error_file = self.storage_dir / f"{media_id}_error.json"
            if not error_file.exists():
                return None
                
            async with aiofiles.open(error_file, 'r') as f:
                error_data = json.loads(await f.read())
                return error_data.get("error")
                
        except Exception as e:
            self.logger.error(f"Failed to get error: {str(e)}")
            return None

    async def add_to_queue(self, media_id: str, task_type: str, **kwargs):
        """
        Add a processing task to the queue
        """
        try:
            task = {
                "media_id": media_id,
                "type": task_type,
                "params": kwargs,
                "created_at": datetime.utcnow().isoformat()
            }
            
            await self.processing_queue.put(task)
            await self.update_status(media_id, "queued")
            
        except Exception as e:
            self.logger.error(f"Failed to add task to queue: {str(e)}")
            raise

    async def _process_queue(self):
        """
        Process tasks from the queue
        """
        while True:
            try:
                task = await self.processing_queue.get()
                media_id = task["media_id"]
                
                # Update status to processing
                await self.update_status(media_id, "processing")
                
                # Process based on task type
                if task["type"] == "ocr":
                    result = await self.ocr_service.process_image(
                        task["params"]["image_path"]
                    )
                elif task["type"] == "transcription":
                    result = await self.voice_service.transcribe_audio(
                        task["params"]["audio_path"],
                        task["params"].get("language", "en-US")
                    )
                elif task["type"] == "image_analysis":
                    result = await self.image_service.analyze_image(
                        task["params"]["image_path"]
                    )
                else:
                    raise ValueError(f"Unknown task type: {task['type']}")
                
                # Store results
                await self.store_result(media_id, result)
                await self.update_status(media_id, "completed")
                
            except Exception as e:
                self.logger.error(f"Task processing failed: {str(e)}")
                if media_id:
                    await self.store_error(media_id, str(e))
                    await self.update_status(media_id, "failed")
                    
            finally:
                self.processing_queue.task_done()

    async def cancel_processing(self, media_id: str):
        """
        Cancel processing of a media file
        """
        try:
            # Update status to cancelled
            await self.update_status(media_id, "cancelled")
            
            # Remove any pending tasks for this media_id
            tasks = [t for t in self.processing_queue._queue if t["media_id"] != media_id]
            self.processing_queue._queue.clear()
            for task in tasks:
                await self.processing_queue.put(task)
                
        except Exception as e:
            self.logger.error(f"Failed to cancel processing: {str(e)}")
            raise

    async def cleanup_old_files(self, max_age_days: int = 7):
        """
        Clean up old processing files
        """
        try:
            current_time = datetime.utcnow()
            
            for file in self.storage_dir.glob("*_status.json"):
                async with aiofiles.open(file, 'r') as f:
                    status_data = json.loads(await f.read())
                    updated_at = datetime.fromisoformat(status_data["updated_at"])
                    
                    if (current_time - updated_at).days > max_age_days:
                        media_id = file.stem.replace("_status", "")
                        await self._cleanup_media_files(media_id)
                        
        except Exception as e:
            self.logger.error(f"Failed to cleanup old files: {str(e)}")
            raise

    async def _cleanup_media_files(self, media_id: str):
        """
        Clean up all files related to a media item
        """
        try:
            files = [
                f"{media_id}_status.json",
                f"{media_id}_result.json",
                f"{media_id}_error.json"
            ]
            
            for file in files:
                file_path = self.storage_dir / file
                if file_path.exists():
                    os.remove(file_path)
                    
        except Exception as e:
            self.logger.error(f"Failed to cleanup media files: {str(e)}")
            raise 