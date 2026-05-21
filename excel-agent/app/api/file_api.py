from fastapi import APIRouter, UploadFile, HTTPException

from app.core.config import settings
from app.services.file_service import save_upload

router = APIRouter(prefix="/api/files", tags=["files"])


@router.post("/upload")
async def upload_file(file: UploadFile):
    if not file.filename.endswith((".xlsx", ".xls", ".csv")):
        raise HTTPException(status_code=400, detail="Only Excel/CSV files are supported")

    saved_path = await save_upload(file)
    return {"filename": file.filename, "path": saved_path}
