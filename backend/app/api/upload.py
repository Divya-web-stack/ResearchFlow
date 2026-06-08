import os
import uuid
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, HTTPException
from app.models.schemas import UploadResponse

router = APIRouter(tags=["upload"])
UPLOAD_DIR = Path(__file__).resolve().parents[2] / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

@router.post("/", response_model=UploadResponse)
async def upload_file(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")

    upload_id = str(uuid.uuid4())
    destination = UPLOAD_DIR / f"{upload_id}_{file.filename}"
    contents = await file.read()
    destination.write_bytes(contents)

    return UploadResponse(
        upload_id=upload_id,
        filename=file.filename,
        message="File uploaded successfully.",
    )
