from fastapi import FastAPI, UploadFile, HTTPException, FileResponse, Query
from tasks import process_audio_task
import uuid
import shutil
import os
from typing import Dict, Literal

from s3_storage import s3_storage
from status_tracker import status_tracker

app = FastAPI()

@app.post("/upload/")
async def upload_audio(
    file: UploadFile,
    num_speakers: int | None = Query(None, description="Expected number of speakers in the audio"),
    language: str | None = Query(None, description="Language of the audio file")
) -> Dict[str, str]:
    task_id = str(uuid.uuid4())
    
    # Create uploads directory if it doesn't exist
    os.makedirs("uploads", exist_ok=True)
    
    # Save file locally
    filepath = f"uploads/{task_id}_{file.filename}"
    with open(filepath, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Set initial status
    status_tracker.set_status(task_id, "uploaded", {"filename": file.filename})
    
    # Start processing task
    process_audio_task.delay(filepath, task_id, num_speakers, language)
    
    return {
        "task_id": task_id,
        "status": "processing",
        "message": "File uploaded successfully, processing started"
    }

@app.get("/status/{task_id}")
async def get_status(task_id: str) -> Dict:
    status_data = status_tracker.get_status(task_id)
    if not status_data:
        raise HTTPException(status_code=404, detail="Task not found")
    return status_data

@app.get("/download/{task_id}")
async def get_download_link(
    task_id: str,
    format: Literal["md", "txt"] = Query("txt", description="Format of the summary file")
) -> Dict:
    status_data = status_tracker.get_status(task_id)
    if not status_data:
        raise HTTPException(status_code=404, detail="Task not found")
    
    if status_data["status"] != "completed":
        raise HTTPException(
            status_code=400,
            detail=f"Task is not ready for download. Current status: {status_data['status']}"
        )
    
    # Get the S3 key for the requested format
    s3_keys = status_data["details"].get("s3_keys", {})
    s3_key = s3_keys.get(format)
    if not s3_key:
        raise HTTPException(
            status_code=404,
            detail=f"Download link not found for format: {format}"
        )
    
    # Generate presigned URL
    download_url = s3_storage.get_download_url(s3_key)
    if not download_url:
        raise HTTPException(status_code=500, detail="Failed to generate download URL")
    
    return {
        "download_url": download_url,
        "format": format,
        "expires_in": "1 hour"
    }