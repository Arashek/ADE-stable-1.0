from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from typing import List, Optional
import aiofiles
import os
from datetime import datetime
import uuid
from pathlib import Path

from ..services.ocr_service import OCRService
from ..services.voice_transcription import VoiceTranscriptionService
from ..services.image_analysis import ImageAnalysisService
from ..orchestrator.media_router import MediaRouter

router = APIRouter(prefix="/api/media", tags=["media"])

# Initialize services
ocr_service = OCRService()
voice_service = VoiceTranscriptionService()
image_service = ImageAnalysisService()
media_router = MediaRouter()

# Configure upload directory
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

@router.post("/upload/image")
async def upload_image(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    process_ocr: bool = True,
    analyze_image: bool = True
):
    """Handle image upload and processing"""
    try:
        # Validate file type
        if not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="Invalid file type")

        # Generate unique filename
        file_extension = os.path.splitext(file.filename)[1]
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        file_path = UPLOAD_DIR / unique_filename

        # Save file
        async with aiofiles.open(file_path, 'wb') as out_file:
            content = await file.read()
            await out_file.write(content)

        # Create media record
        media_id = str(uuid.uuid4())
        media_record = {
            "id": media_id,
            "filename": unique_filename,
            "original_name": file.filename,
            "content_type": file.content_type,
            "size": len(content),
            "uploaded_at": datetime.utcnow().isoformat(),
            "status": "processing"
        }

        # Schedule background processing
        background_tasks.add_task(
            process_image,
            media_id,
            file_path,
            process_ocr,
            analyze_image
        )

        return JSONResponse({
            "message": "File uploaded successfully",
            "media_id": media_id,
            "status": "processing"
        })

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/upload/voice")
async def upload_voice(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    language: Optional[str] = "en-US"
):
    """Handle voice recording upload and transcription"""
    try:
        # Validate file type
        if not file.content_type.startswith('audio/'):
            raise HTTPException(status_code=400, detail="Invalid file type")

        # Generate unique filename
        file_extension = os.path.splitext(file.filename)[1]
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        file_path = UPLOAD_DIR / unique_filename

        # Save file
        async with aiofiles.open(file_path, 'wb') as out_file:
            content = await file.read()
            await out_file.write(content)

        # Create media record
        media_id = str(uuid.uuid4())
        media_record = {
            "id": media_id,
            "filename": unique_filename,
            "original_name": file.filename,
            "content_type": file.content_type,
            "size": len(content),
            "uploaded_at": datetime.utcnow().isoformat(),
            "status": "processing"
        }

        # Schedule background processing
        background_tasks.add_task(
            process_voice,
            media_id,
            file_path,
            language
        )

        return JSONResponse({
            "message": "File uploaded successfully",
            "media_id": media_id,
            "status": "processing"
        })

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status/{media_id}")
async def get_processing_status(media_id: str):
    """Get the processing status of a media file"""
    try:
        status = await media_router.get_status(media_id)
        return JSONResponse({"status": status})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/result/{media_id}")
async def get_processing_result(media_id: str):
    """Get the processing results of a media file"""
    try:
        result = await media_router.get_result(media_id)
        return JSONResponse(result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def process_image(media_id: str, file_path: Path, process_ocr: bool, analyze_image: bool):
    """Process uploaded image file"""
    try:
        # Update status to processing
        await media_router.update_status(media_id, "processing")

        results = {}
        
        # Process OCR if requested
        if process_ocr:
            ocr_result = await ocr_service.process_image(file_path)
            results["ocr"] = ocr_result

        # Analyze image if requested
        if analyze_image:
            analysis_result = await image_service.analyze_image(file_path)
            results["analysis"] = analysis_result

        # Update status and store results
        await media_router.update_status(media_id, "completed")
        await media_router.store_result(media_id, results)

    except Exception as e:
        await media_router.update_status(media_id, "failed")
        await media_router.store_error(media_id, str(e))

async def process_voice(media_id: str, file_path: Path, language: str):
    """Process uploaded voice recording"""
    try:
        # Update status to processing
        await media_router.update_status(media_id, "processing")

        # Transcribe audio
        transcription_result = await voice_service.transcribe_audio(file_path, language)
        
        # Update status and store results
        await media_router.update_status(media_id, "completed")
        await media_router.store_result(media_id, {
            "transcription": transcription_result
        })

    except Exception as e:
        await media_router.update_status(media_id, "failed")
        await media_router.store_error(media_id, str(e)) 